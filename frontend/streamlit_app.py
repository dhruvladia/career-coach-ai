import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="LearnTube AI Career Coach",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat UI
st.markdown("""
<style>
.stChatFloatingInputContainer {
    position: sticky;
    bottom: 0;
    background-color: white;
    z-index: 999;
}
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
.user-message {
    background-color: #e3f2fd;
    margin-left: 2rem;
}
.assistant-message {
    background-color: #f5f5f5;
    margin-right: 2rem;
}
.profile-info {
    background-color: #f0f7ff;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile_data" not in st.session_state:
    st.session_state.profile_data = None

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {}

def start_new_session(linkedin_url: str):
    """Start a new career coaching session"""
    with st.spinner("Starting your career coaching session..."):
        result = make_api_request(
            "/start_session",
            method="POST",
            data={"linkedin_url": linkedin_url}
        )
        
        if result:
            st.session_state.session_id = result.get("session_id")
            st.session_state.profile_data = result.get("profile_data")
            # Add welcome message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.get("message", "Welcome to your AI Career Coach!"),
                "timestamp": datetime.now().isoformat()
            })
            st.rerun()

def send_message(message: str):
    """Send a message to the AI career coach"""
    if not st.session_state.session_id:
        st.error("Please start a session first!")
        return
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Send to backend
    with st.spinner("AI Career Coach is thinking..."):
        result = make_api_request(
            "/chat",
            method="POST",
            data={
                "session_id": st.session_state.session_id,
                "message": message
            }
        )
        
        if result:
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.get("message", "Sorry, I couldn't process that."),
                "timestamp": datetime.now().isoformat(),
                "agent_type": result.get("agent_type"),
                "job_fit_analysis": result.get("job_fit_analysis"),
                "career_path": result.get("career_path")
            })
            
            # Update profile if changed
            if result.get("profile_updated"):
                load_profile()

def load_profile():
    """Load user profile from backend"""
    if st.session_state.session_id:
        result = make_api_request(f"/profile/{st.session_state.session_id}")
        if result:
            st.session_state.profile_data = result

def display_profile_summary():
    """Display user profile summary in sidebar"""
    if st.session_state.profile_data:
        profile = st.session_state.profile_data
        st.sidebar.markdown("### 👤 Your Profile")
        
        if profile.get("name"):
            st.sidebar.markdown(f"**Name:** {profile['name']}")
        
        if profile.get("about"):
            with st.sidebar.expander("About", expanded=False):
                st.write(profile["about"][:200] + "..." if len(profile.get("about", "")) > 200 else profile.get("about", ""))
        
        if profile.get("skills"):
            with st.sidebar.expander(f"Skills ({len(profile['skills'])})", expanded=False):
                for skill in profile["skills"][:10]:
                    st.write(f"• {skill}")
                if len(profile["skills"]) > 10:
                    st.write(f"... and {len(profile['skills']) - 10} more")
        
        if profile.get("experience"):
            with st.sidebar.expander(f"Experience ({len(profile['experience'])} positions)", expanded=False):
                for exp in profile["experience"][:3]:
                    st.write(f"**{exp.get('title', 'N/A')}**")
                    st.write(f"{exp.get('company', 'N/A')}")
                    st.write("---")

# Main app
st.title("🚀 LearnTube AI Career Coach")

# Sidebar
st.sidebar.title("Career Coaching Session")

# Session management
if not st.session_state.session_id:
    st.sidebar.markdown("### Start Your Session")
    st.sidebar.markdown("Enter your LinkedIn profile URL to begin:")
    
    linkedin_url = st.sidebar.text_input(
        "LinkedIn URL",
        placeholder="https://linkedin.com/in/yourprofile",
        help="We'll analyze your profile to provide personalized career guidance"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Start Session", type="primary", use_container_width=True):
            if linkedin_url:
                start_new_session(linkedin_url)
            else:
                st.sidebar.error("Please enter a LinkedIn URL")
    
    with col2:
        if st.button("Skip LinkedIn", use_container_width=True):
            # Start session without LinkedIn
            start_new_session("https://linkedin.com/in/manual-entry")
    
    # Welcome message for new users
    st.markdown("""
    ### Welcome to Your AI-Powered Career Coach! 🎯
    
    I'm here to help you with:
    - 📊 **Job Fit Analysis** - Analyze job descriptions against your profile
    - 🛤️ **Career Path Guidance** - Get personalized career advice
    - 📝 **Profile Enhancement** - Improve your LinkedIn presence
    - 🎓 **Skills Development** - Identify growth opportunities
    
    **Get started by entering your LinkedIn URL in the sidebar!**
    """)
    
else:
    # Active session
    st.sidebar.success(f"Session Active")
    st.sidebar.caption(f"Session ID: {st.session_state.session_id[:8]}...")
    
    # Display profile summary
    display_profile_summary()
    
    # New session button
    if st.sidebar.button("Start New Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    # Chat interface
    st.markdown("### 💬 Chat with Your AI Career Coach")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display additional info for assistant messages
            if message["role"] == "assistant":
                if message.get("job_fit_analysis"):
                    with st.expander("📊 Job Fit Analysis Details"):
                        analysis = message["job_fit_analysis"]
                        st.markdown(f"**Match Score:** {analysis.get('score', 'N/A')}%")
                        st.markdown(f"**Summary:** {analysis.get('summary', 'N/A')}")
                        
                        # Display missing skills if available
                        if analysis.get('missing_skills'):
                            st.markdown("**Missing Skills:**")
                            for skill in analysis['missing_skills']:
                                st.markdown(f"• {skill}")
                        
                        # Display enhancement suggestions if available
                        if analysis.get('enhancements'):
                            st.markdown("**Enhancement Suggestions:**")
                            for enhancement in analysis['enhancements']:
                                st.markdown(f"• {enhancement}")
                
                if message.get("career_path"):
                    with st.expander("🛤️ Career Path Recommendations"):
                        st.write(message["career_path"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your career..."):
        send_message(prompt)
        st.rerun()
    
    # Quick action buttons
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Analyze Job", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "I'd like to analyze a job description. Let me paste it for you.",
                "timestamp": datetime.now().isoformat()
            })
            st.rerun()
    
    with col2:
        if st.button("📝 Improve Profile", use_container_width=True):
            send_message("How can I improve my LinkedIn profile to stand out more?")
            st.rerun()
    
    with col3:
        if st.button("🎯 Career Path", use_container_width=True):
            send_message("What career paths would you recommend for me based on my profile?")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Powered by LearnTube AI | Your Personal Career Coach 🚀</div>",
    unsafe_allow_html=True
) 