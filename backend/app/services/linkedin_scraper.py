from apify_client import ApifyClient
from typing import Dict, Any, Optional, List
import time
import json

from app.config import settings

class LinkedInScraper:
    def __init__(self):
        # Initialize the ApifyClient with API token
        self.client = ApifyClient(settings.apify_api_token)
        self.actor_id = "2SyF0bVxmgGr8IVCZ"  # New LinkedIn Profile Scraper Actor
    
    def scrape_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape LinkedIn profile data using Apify
        Returns structured profile data or None if failed
        """
        try:
            # Prepare Actor input - using the new format
            run_input = {
                "profileUrls": [linkedin_url]
            }
            
            print(f"Starting Apify actor run for: {linkedin_url}")
            
            # Run the Actor and wait for it to finish
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch and process Actor results from the run's dataset
            print(f"Fetching results from dataset: {run['defaultDatasetId']}")
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if items:
                print(f"Found {len(items)} profile(s)")
                profile_data = items[0]  # Get the first (and usually only) profile
                return self._process_profile_data(profile_data)
            else:
                print("No profile data found in the dataset")
            
            return None
            
        except Exception as e:
            print(f"Error scraping LinkedIn profile: {e}")
            return None
    
    def _process_profile_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the raw Apify data into our schema
        Note: The data structure may vary depending on the actor's output format
        """
        # Debug: Print the raw data structure to understand the format
        print(f"Raw data keys: {list(raw_data.keys())}")
        
        # Common field mappings - adjust based on actual actor output
        processed_data = {
            "name": raw_data.get("name") or raw_data.get("fullName") or "",
            "about": raw_data.get("about") or raw_data.get("summary") or "",
            "skills": self._extract_skills(raw_data),
            "experience": self._extract_experience(raw_data),
            "education": self._extract_education(raw_data),
            "location": raw_data.get("location") or "",
            "headline": raw_data.get("headline") or raw_data.get("title") or "",
            "connections": raw_data.get("connections") or raw_data.get("connectionsCount") or 0,
            "profilePicture": raw_data.get("profilePicture") or raw_data.get("photo") or "",
        }
        
        return processed_data
    
    def _extract_skills(self, data: Dict[str, Any]) -> List[str]:
        """Extract skills from the profile data"""
        skills = []
        
        # Try different possible field names
        skill_fields = ["skills", "skillsList", "userSkills"]
        
        for field in skill_fields:
            if field in data and isinstance(data[field], list):
                for skill in data[field]:
                    if isinstance(skill, dict):
                        # Try different key names for skill name
                        skill_name = skill.get("name") or skill.get("skill") or skill.get("title")
                        if skill_name:
                            skills.append(skill_name)
                    elif isinstance(skill, str):
                        skills.append(skill)
                break
        
        return skills[:20]  # Limit to top 20 skills
    
    def _extract_experience(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract work experience from the profile data"""
        experience = []
        
        # Try different possible field names
        exp_fields = ["experience", "positions", "workExperience", "jobs"]
        
        for field in exp_fields:
            if field in data and isinstance(data[field], list):
                for position in data[field]:
                    exp = {
                        "title": position.get("title") or position.get("position") or "",
                        "company": position.get("company") or position.get("companyName") or "",
                        "duration": self._format_duration(position),
                        "description": position.get("description") or "",
                        "location": position.get("location") or "",
                    }
                    experience.append(exp)
                break
        
        return experience[:10]  # Limit to last 10 positions
    
    def _extract_education(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract education from the profile data"""
        education = []
        
        # Try different possible field names
        edu_fields = ["education", "schools", "educationList"]
        
        for field in edu_fields:
            if field in data and isinstance(data[field], list):
                for school in data[field]:
                    edu = {
                        "institution": school.get("school") or school.get("schoolName") or school.get("institution") or "",
                        "degree": school.get("degree") or school.get("degreeName") or "",
                        "field": school.get("field") or school.get("fieldOfStudy") or "",
                        "duration": self._format_education_duration(school),
                    }
                    education.append(edu)
                break
        
        return education
    
    def _format_duration(self, position: Dict[str, Any]) -> str:
        """Format work duration from position data"""
        # Try different date field formats
        start_date = position.get("startDate") or position.get("start") or ""
        end_date = position.get("endDate") or position.get("end") or "Present"
        
        # Handle date objects if they exist
        if isinstance(start_date, dict):
            start_date = f"{start_date.get('month', '')}/{start_date.get('year', '')}"
        if isinstance(end_date, dict):
            end_date = f"{end_date.get('month', '')}/{end_date.get('year', '')}"
        
        if start_date:
            return f"{start_date} - {end_date}"
        
        # Try duration field if dates are not available
        return position.get("duration") or ""
    
    def _format_education_duration(self, school: Dict[str, Any]) -> str:
        """Format education duration from school data"""
        start_year = school.get("startYear") or school.get("start") or ""
        end_year = school.get("endYear") or school.get("end") or ""
        
        if start_year and end_year:
            return f"{start_year} - {end_year}"
        elif start_year:
            return f"{start_year} - Present"
        
        # Try duration field if years are not available
        return school.get("duration") or ""

# Create a singleton instance
linkedin_scraper = LinkedInScraper() 