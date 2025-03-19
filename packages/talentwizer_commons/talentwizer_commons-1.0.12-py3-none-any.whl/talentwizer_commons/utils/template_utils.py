import logging
from typing import Optional, Dict
from talentwizer_commons.app.engine import get_chat_engine

logger = logging.getLogger(__name__)

async def process_ai_commands(commands: list, profile: dict, chat_engine=None) -> str:
    """Process AI commands to generate personalized content."""
    try:
        if not chat_engine:
            chat_engine = get_chat_engine()
            
        prompt = f"""
        As a recruiting expert, analyze this candidate profile and {' '.join(commands)}
        Profile Summary: {profile.get('summary', '')}
        Current Role: {profile.get('experience', [{}])[0].get('title', '')}
        Skills: {', '.join(profile.get('skills', []))}
        """
        
        response = chat_engine.chat(prompt)
        return response.response

    except Exception as e:
        logger.error(f"Error in process_ai_commands: {str(e)}", exc_info=True)
        return "[Error processing AI command]"

async def populate_template_v2(template: str, person: dict, job_title: str, client_info: Optional[Dict] = None) -> str:
    """Process template with variables and AI commands."""
    try:
        variables = {
            "Full Name": person.get("full_name", ""),
            "First Name": person.get("full_name", "").split()[0] if person.get("full_name") else "",
            "Current Company": person.get("experience", [{}])[0].get("company_name", ""),
            "Current Job Title": person.get("experience", [{}])[0].get("title", ""),
            "Client Job Title": job_title,
            "Client Company": client_info.get("companyName", "our company") if client_info else "our company",  
            "User Name": client_info.get("userName", "") if client_info else ""
        }

        populated = template
        for var, value in variables.items():
            populated = populated.replace(f"{{{{{var}}}}}", str(value or ""))

        # Process AI commands if needed 
        import re
        ai_matches = re.finditer(r'\{\{AI:([^}]+)\}\}', populated)
        for match in ai_matches:
            command = match.group(1)
            ai_content = await process_ai_commands([command], person)
            populated = populated.replace(match.group(0), ai_content)

        return populated

    except Exception as e:
        logger.error(f"Error in populate_template_v2: {str(e)}", exc_info=True)
        raise
