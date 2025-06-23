from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

from app.config import settings
from app.agents.state import GraphState

class ContentEnhancementAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.4
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional LinkedIn content strategist and copywriter. You help professionals optimize their LinkedIn profiles to attract recruiters and opportunities.

Your expertise includes:
- Writing compelling professional summaries/about sections
- Crafting impactful headlines
- Optimizing experience descriptions with metrics and achievements
- Using industry keywords for better visibility
- Following LinkedIn best practices

Guidelines:
- Use action verbs and quantifiable results when possible
- Include relevant industry keywords
- Write in first person for about sections
- Keep tone professional yet personable
- Focus on value proposition and achievements
- Avoid buzzwords and clichés
- Make content ATS-friendly

Response format:
- Provide specific, actionable content suggestions
- Use clear headings for different sections
- Include examples and templates
- Explain why changes improve the profile"""),
            ("human", """User Profile:
{profile_data}

User's Request:
{user_query}

Please provide content enhancement suggestions based on their profile and specific request.""")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def enhance_content(self, state: GraphState) -> GraphState:
        """Provide content enhancement suggestions for LinkedIn profile"""
        
        profile_data = state["user_profile_data"]
        user_query = state["current_user_query"]
        
        try:
            # Format profile data for analysis
            formatted_profile = self._format_profile_for_enhancement(profile_data)
            
            # Generate content enhancement suggestions
            enhancement = self.chain.invoke({
                "profile_data": formatted_profile,
                "user_query": user_query
            })
            
            # Store response
            state["final_response"] = enhancement
            state["agent_type"] = "content_enhancement"
            state["content_enhancement_result"] = enhancement
            
        except Exception as e:
            print(f"Error in content enhancement: {e}")
            state["final_response"] = self._get_fallback_enhancement_response(user_query)
            state["agent_type"] = "content_enhancement"
        
        return state
    
    def _format_profile_for_enhancement(self, profile_data: Dict[str, Any]) -> str:
        """Format profile data for content enhancement analysis"""
        formatted = []
        
        # Current headline
        if profile_data.get("headline"):
            formatted.append(f"Current Headline: {profile_data['headline']}")
        else:
            formatted.append("Current Headline: [Not provided]")
        
        # Current about section
        if profile_data.get("about"):
            formatted.append(f"Current About Section:\n{profile_data['about']}")
        else:
            formatted.append("Current About Section: [Not provided]")
        
        # Skills
        if profile_data.get("skills"):
            skills_str = ", ".join(profile_data["skills"][:10])
            formatted.append(f"Key Skills: {skills_str}")
        
        # Experience for context
        if profile_data.get("experience"):
            formatted.append("Recent Experience:")
            for i, exp in enumerate(profile_data["experience"][:3]):
                exp_info = f"  {i+1}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}"
                if exp.get("duration"):
                    exp_info += f" ({exp['duration']})"
                formatted.append(exp_info)
                
                if exp.get("description"):
                    formatted.append(f"     Description: {exp['description'][:200]}...")
        
        # Education for context
        if profile_data.get("education"):
            formatted.append("Education:")
            for edu in profile_data["education"][:2]:
                edu_info = f"  - {edu.get('degree', '')} {edu.get('field', '')} from {edu.get('institution', '')}"
                formatted.append(edu_info)
        
        return "\n".join(formatted)
    
    def _get_fallback_enhancement_response(self, user_query: str) -> str:
        """Provide fallback content enhancement suggestions"""
        return """# LinkedIn Profile Enhancement Guide

I'd be happy to help you improve your LinkedIn profile! Here are some general areas I can assist with:

## 🎯 Profile Sections I Can Optimize:

**Professional Headline**
- Craft compelling, keyword-rich headlines
- Include your value proposition
- Make it recruiter-friendly

**About Section**
- Write engaging professional summaries
- Highlight key achievements and skills
- Include industry keywords
- Tell your professional story

**Experience Descriptions**
- Add quantifiable achievements
- Use action verbs and metrics
- Optimize for ATS systems
- Highlight key accomplishments

**Skills & Keywords**
- Identify relevant industry keywords
- Optimize for search visibility
- Align with target roles

## 💡 How to Get Started:

1. **Share your current content** - paste your existing headline, about section, or experience descriptions
2. **Tell me your goals** - what type of roles are you targeting?
3. **Mention your industry** - so I can suggest relevant keywords

**Example requests:**
- "Help me rewrite my LinkedIn headline"
- "Improve my about section for data science roles"
- "Make my experience descriptions more impactful"

What specific part of your profile would you like to enhance?"""

# Create agent instance
content_enhancement_agent = ContentEnhancementAgent() 