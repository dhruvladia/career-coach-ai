from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any, List

from app.config import settings
from app.agents.state import GraphState

class CareerPathAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.3
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are CareerPath-GPT, a pragmatic and experienced career counselor. You provide realistic, actionable career guidance based on a user's current profile and goals.

Your approach:
1. Analyze the gap between their current role/skills and their desired goal
2. If the goal is realistic with their timeline, provide a step-by-step career trajectory
3. If the goal is unrealistic (e.g., Junior Developer to CTO in 2 years), you MUST state that the timeline is ambitious and provide a more realistic trajectory
4. Always be encouraging but ground expectations in reality
5. Provide specific, actionable advice
6. Suggest 5 key areas for upskilling

Response format:
- Use clear, encouraging markdown
- Include specific milestones with timeframes
- Provide actionable next steps
- Be honest about challenges while staying positive
- Focus on practical advice over generic platitudes"""),
            ("human", """Current User Profile:
{profile_data}

User's Career Question/Goal:
{user_query}

Chat History Context:
{chat_history}

Please provide comprehensive career guidance.""")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def provide_career_guidance(self, state: GraphState) -> GraphState:
        """Provide career path guidance based on user profile and query"""
        
        profile_data = state["user_profile_data"]
        user_query = state["current_user_query"]
        
        # Get recent chat history for context
        recent_history = []
        if state.get("chat_history"):
            recent_history = state["chat_history"][-4:]
        
        try:
            # Format profile data for analysis
            formatted_profile = self._format_profile_for_guidance(profile_data)
            
            # Generate career guidance
            guidance = self.chain.invoke({
                "profile_data": formatted_profile,
                "user_query": user_query,
                "chat_history": "\n".join([f"{msg.type}: {msg.content}" for msg in recent_history])
            })
            
            # Store response
            state["final_response"] = guidance
            state["agent_type"] = "career_path"
            
            # Extract key information for structured storage
            state["career_path_response"] = {
                "analysis": guidance[:500] + "..." if len(guidance) > 500 else guidance,
                "trajectory": "Generated career trajectory",
                "upskilling_areas": self._extract_upskilling_areas(guidance)
            }
            
        except Exception as e:
            print(f"Error in career path guidance: {e}")
            state["final_response"] = self._get_fallback_response(user_query)
            state["agent_type"] = "career_path"
        
        return state
    
    def _format_profile_for_guidance(self, profile_data: Dict[str, Any]) -> str:
        """Format profile data for career guidance analysis"""
        formatted = []
        
        # Basic info
        if profile_data.get("name"):
            formatted.append(f"Name: {profile_data['name']}")
        
        if profile_data.get("headline"):
            formatted.append(f"Current Role/Headline: {profile_data['headline']}")
        
        # Professional summary
        if profile_data.get("about"):
            formatted.append(f"Professional Summary: {profile_data['about'][:300]}...")
        
        # Skills
        if profile_data.get("skills"):
            skills_str = ", ".join(profile_data["skills"][:15])  # Top 15 skills
            formatted.append(f"Key Skills: {skills_str}")
        
        # Experience analysis
        if profile_data.get("experience"):
            formatted.append("Professional Experience:")
            
            # Calculate total experience
            total_years = self._estimate_experience_years(profile_data["experience"])
            formatted.append(f"  Estimated Total Experience: ~{total_years} years")
            
            # Recent positions
            for i, exp in enumerate(profile_data["experience"][:3]):
                role_info = f"  {i+1}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}"
                if exp.get("duration"):
                    role_info += f" ({exp['duration']})"
                formatted.append(role_info)
                
                if exp.get("description"):
                    formatted.append(f"     Key responsibilities: {exp['description'][:150]}...")
        
        # Education
        if profile_data.get("education"):
            formatted.append("Education:")
            for edu in profile_data["education"][:2]:
                edu_info = f"  - {edu.get('degree', 'N/A')} in {edu.get('field', 'N/A')} from {edu.get('institution', 'N/A')}"
                formatted.append(edu_info)
        
        return "\n".join(formatted)
    
    def _estimate_experience_years(self, experience_list: List[Dict[str, Any]]) -> int:
        """Estimate total years of experience from experience list"""
        # Simple estimation - count number of positions and assume average duration
        if not experience_list:
            return 0
        
        # If we have duration info, try to parse it
        total_months = 0
        positions_with_duration = 0
        
        for exp in experience_list:
            duration = exp.get("duration", "")
            if duration and "year" in duration.lower():
                # Extract years from duration string
                try:
                    years = int(''.join(filter(str.isdigit, duration.split("year")[0])))
                    total_months += years * 12
                    positions_with_duration += 1
                except:
                    pass
        
        if positions_with_duration > 0:
            return max(1, total_months // 12)
        else:
            # Fallback: assume 2 years per position for first 3 positions, 1.5 for others
            years = min(len(experience_list), 3) * 2 + max(0, len(experience_list) - 3) * 1.5
            return max(1, int(years))
    
    def _extract_upskilling_areas(self, guidance_text: str) -> List[str]:
        """Extract upskilling areas from the guidance text"""
        # Simple extraction - look for common patterns
        upskilling_areas = []
        
        # Common skill categories
        tech_skills = ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", 
                      "Machine Learning", "Data Science", "DevOps", "Cloud Computing"]
        
        soft_skills = ["Leadership", "Communication", "Project Management", "Strategic Thinking", 
                      "Team Management", "Negotiation", "Public Speaking"]
        
        # Look for mentions in the text
        guidance_lower = guidance_text.lower()
        
        for skill in tech_skills + soft_skills:
            if skill.lower() in guidance_lower:
                upskilling_areas.append(skill)
        
        # Limit to 5 and add some defaults if none found
        if not upskilling_areas:
            upskilling_areas = ["Industry Knowledge", "Technical Skills", "Leadership", 
                              "Communication", "Strategic Thinking"]
        
        return upskilling_areas[:5]
    
    def _get_fallback_response(self, user_query: str) -> str:
        """Provide a fallback response when the main agent fails"""
        return f"""I understand you're looking for career guidance. While I encountered a technical issue processing your specific request, I'd be happy to help you with:

## 🎯 Career Planning Areas I Can Assist With:

**Career Trajectory Planning**
- Moving from your current role to your target position
- Realistic timelines and milestones
- Skills gap analysis

**Professional Development**
- Key skills to develop for your goals
- Learning resources and paths
- Industry insights and trends

**Job Search Strategy**
- Resume and LinkedIn optimization
- Interview preparation
- Networking advice

**Career Transitions**
- Changing industries or roles
- Leveraging transferable skills
- Managing career pivots

---

Please try rephrasing your question or let me know specifically what aspect of your career you'd like to focus on. I'm here to provide practical, actionable guidance based on your background and goals!"""

# Create agent instance
career_path_agent = CareerPathAgent() 