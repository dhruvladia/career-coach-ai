from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import json

from app.config import settings
from app.agents.state import GraphState

class JobFitAnalysis(BaseModel):
    score: int = Field(description="Job fit score as percentage (0-100)")
    summary: str = Field(description="2-sentence summary of fit")
    missing_skills: List[str] = Field(description="Up to 5 missing skills from job description")
    enhancements: List[str] = Field(description="Up to 3 profile enhancement suggestions")

class JobFitAnalyst:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.1
        )
        
        self.parser = JsonOutputParser(pydantic_object=JobFitAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are JobFit-GPT, an expert tech recruiter and career coach. You will analyze a user's professional profile against a job description.

Your task is to:
1. Calculate a 'Job Fit Score' as a percentage (0-100) based ONLY on skills alignment and experience level
2. Provide a brief, 2-sentence summary of why they are or are not a good fit
3. List up to 5 'Missing Skills' from the job description that are not in their profile
4. List up to 3 'Profile Enhancement Suggestions' to better align their experience with the job requirements

Scoring Guidelines:
- 90-100%: Perfect match with all key skills and experience level
- 80-89%: Strong match with most skills, minor gaps
- 70-79%: Good match with some important skills missing
- 60-69%: Moderate match with several key skills missing
- 50-59%: Basic match with significant skill gaps
- Below 50%: Poor match with major skill/experience gaps

{format_instructions}"""),
            ("human", """User Profile:
{profile_data}

Job Description:
{job_description}

Please analyze the job fit and provide your assessment.""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze_job_fit(self, state: GraphState) -> GraphState:
        """Analyze job fit between user profile and job description"""
        
        profile_data = state["user_profile_data"]
        user_query = state["current_user_query"]
        
        # Extract job description from user query
        job_description = self._extract_job_description(user_query)
        
        if not job_description:
            # No job description found, provide guidance on what's needed
            state["final_response"] = """I'd be happy to analyze a job fit for you! Please paste the job description you'd like me to analyze against your profile. 

You can share:
- The full job posting
- Just the requirements section
- Key skills and qualifications listed

Once you provide the job details, I'll give you:
✅ A detailed fit score (0-100%)
✅ Analysis of your strengths for this role
✅ Specific skills you might be missing
✅ Suggestions to improve your profile for better alignment"""
            
            state["agent_type"] = "job_fit_analyst"
            return state
        
        try:
            # Format profile data for analysis
            formatted_profile = self._format_profile_for_analysis(profile_data)
            
            # Analyze the job fit
            analysis = self.chain.invoke({
                "profile_data": formatted_profile,
                "job_description": job_description,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Store analysis in state
            state["job_fit_analysis"] = analysis
            
            # Generate response message
            state["final_response"] = self._format_analysis_response(analysis)
            state["agent_type"] = "job_fit_analyst"
            
        except Exception as e:
            print(f"Error in job fit analysis: {e}")
            state["final_response"] = "I encountered an issue analyzing the job fit. Please try rephrasing your request or check if the job description is clear and complete."
            state["agent_type"] = "job_fit_analyst"
        
        return state
    
    def _extract_job_description(self, user_query: str) -> str:
        """Extract job description from user query"""
        # Simple extraction - look for common job posting patterns
        query_lower = user_query.lower()
        
        # Check if it looks like a job description
        job_indicators = [
            "job description", "requirements", "responsibilities", 
            "qualifications", "skills required", "experience required",
            "we are looking for", "position", "role", "hiring"
        ]
        
        if any(indicator in query_lower for indicator in job_indicators):
            return user_query
        
        # If it's a short query asking about job analysis, return empty
        if len(user_query.split()) < 20:
            return ""
        
        return user_query
    
    def _format_profile_for_analysis(self, profile_data: Dict[str, Any]) -> str:
        """Format profile data for LLM analysis"""
        formatted = []
        
        if profile_data.get("name"):
            formatted.append(f"Name: {profile_data['name']}")
        
        if profile_data.get("headline"):
            formatted.append(f"Headline: {profile_data['headline']}")
        
        if profile_data.get("about"):
            formatted.append(f"About: {profile_data['about']}")
        
        if profile_data.get("skills"):
            skills_str = ", ".join(profile_data["skills"])
            formatted.append(f"Skills: {skills_str}")
        
        if profile_data.get("experience"):
            formatted.append("Experience:")
            for exp in profile_data["experience"][:5]:  # Top 5 experiences
                exp_str = f"  - {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}"
                if exp.get("duration"):
                    exp_str += f" ({exp['duration']})"
                if exp.get("description"):
                    exp_str += f"\n    {exp['description'][:200]}..."
                formatted.append(exp_str)
        
        return "\n".join(formatted)
    
    def _format_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis into a user-friendly response"""
        
        score = analysis.get("score", 0)
        summary = analysis.get("summary", "")
        missing_skills = analysis.get("missing_skills", [])
        enhancements = analysis.get("enhancements", [])
        
        # Determine fit level
        if score >= 80:
            fit_level = "🟢 Strong Match"
        elif score >= 60:
            fit_level = "🟡 Good Match"
        else:
            fit_level = "🔴 Needs Development"
        
        response = f"""# Job Fit Analysis Results

## {fit_level} - {score}% Fit Score

{summary}

"""
        
        if missing_skills:
            response += "## 🎯 Skills to Develop\n"
            for skill in missing_skills:
                response += f"• {skill}\n"
            response += "\n"
        
        if enhancements:
            response += "## 💡 Profile Enhancement Tips\n"
            for i, enhancement in enumerate(enhancements, 1):
                response += f"{i}. {enhancement}\n"
            response += "\n"
        
        response += "---\n*Would you like me to help you develop any of these skills or enhance your profile content?*"
        
        return response

# Create agent instance
job_fit_analyst = JobFitAnalyst() 