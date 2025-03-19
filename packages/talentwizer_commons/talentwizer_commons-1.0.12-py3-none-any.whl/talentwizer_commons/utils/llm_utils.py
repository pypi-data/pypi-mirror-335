import logging
from typing import Optional
from talentwizer_commons.app.engine import get_chat_engine
from talentwizer_commons.utils.exceptions import LLMError

logger = logging.getLogger(__name__)

async def generate_profile_summary(profile: dict) -> str:
    """Generate a concise professional summary using LLM."""
    try:
        # Get core information with better fallbacks
        full_name = profile.get('full_name', '')
        current_role = profile.get('headline', '') or f"{profile.get('experience', [{}])[0].get('title', '')} at {profile.get('experience', [{}])[0].get('company_name', '')}"
        
        # Get meaningful experience details
        experiences = []
        for exp in profile.get('experience', [])[:2]:  # Only consider last 2 positions
            if exp and isinstance(exp, dict):
                role = exp.get('title', '')
                company = exp.get('company_name', '')
                exp_summary = exp.get('summary', '').replace('\n', ' ').replace('•', '').strip()
                if role and company:
                    exp_details = f"{role} at {company}"
                    if exp_summary:
                        # Take first sentence or first 100 chars of summary
                        summary_brief = exp_summary.split('.')[0][:100]
                        exp_details += f" where {summary_brief}"
                    experiences.append(exp_details)

        # Get key skills (limit to most relevant)
        key_skills = profile.get('skills', [])[:5]

        prompt = f"""
        Create a professional 2-3 line summary for this person following these rules:
        1. First line must mention their name and current role
        2. Focus on their experience and achievements
        3. Be specific and factual
        4. Avoid technical jargon
        5. Use an active, professional tone
        
        Information:
        Name: {full_name}
        Current Position: {current_role}
        Location: {profile.get('location', '')}
        Recent Experience: {' | '.join(experiences)}
        Key Skills: {', '.join(key_skills)}
        Industry: {profile.get('industry', '')}
        
        Example format:
        "{full_name} is currently a Senior Engineer at [Company], focusing on [key responsibility]. With extensive experience in [domain], they previously [key achievement] at [Previous Company]."
        """

        # Get chat engine instance
        chat_engine = get_chat_engine()
        if not chat_engine:
            raise LLMError("Failed to initialize chat engine")
        
        response = chat_engine.chat(prompt)
        if not response or not response.response:
            raise LLMError("Empty response from LLM")
        
        summary = response.response.strip()
        if not summary or "sorry" in summary.lower():
            # Fallback to template-based summary if LLM fails
            fallback_summary = f"{full_name} is currently {current_role}. With expertise in {', '.join(key_skills[:3])}, they have demonstrated strong capabilities in {profile.get('industry', 'their industry')}."
            return fallback_summary
            
        return summary

    except Exception as e:
        logger.error(f"Error generating profile summary: {str(e)}", exc_info=True)
        return profile.get('summary', '')  # Fallback to original summary
