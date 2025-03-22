from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Optional
import json, os, re
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from supabase import create_client
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()  

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileRequest(BaseModel):
    user_id: str
    email: Optional[str] = None

class PersonalityBucket(Enum):
    ANALYST = "analyst"       # Values precision, logic, data
    CONNECTOR = "connector"   # Values empathy, shared experiences  
    COMMANDER = "commander"   # Values efficiency, results
    EXPLORER = "explorer"     # Values possibilities, innovation

class ConversationStyle(Enum):
    STRUCTURED = "structured"     # Evidence-based, systematic
    STORY_RICH = "story_rich"    # Emotional, narrative-focused
    DIRECT = "direct"            # Solution-focused, brief
    NON_LINEAR = "non_linear"    # Imaginative, exploratory

class EngagementLevel(Enum):
    LOW = 1      # Minimal engagement
    MEDIUM = 2   # Moderate engagement
    HIGH = 3     # Strong engagement
    VERY_HIGH = 4 # Maximum engagement

class ResponseStyle(Enum):
    METRICS_FOCUSED = "metrics"      # Data and research oriented
    FEELINGS_FOCUSED = "feelings"    # Emotion and relationship oriented
    ACTION_FOCUSED = "action"        # Results and solution oriented
    POSSIBILITY_FOCUSED = "possibility" # Innovation and creativity oriented

class ProfessionProfile(BaseModel):
    category: str
    role: str
    experience_years: int
    engagement_level: EngagementLevel

class PersonalityMetrics(BaseModel):
    primary_bucket: PersonalityBucket
    conversation_style: ConversationStyle
    response_style: ResponseStyle
    engagement_score: EngagementLevel
class UserProfile(BaseModel):
    user_id: str
    name: str
    profession: ProfessionProfile
    personality: PersonalityMetrics

    @classmethod
    async def from_signup_answers(cls, user_id: str, signup_answers: dict, openai_client: AsyncOpenAI) -> 'UserProfile':
        """
        Create a UserProfile instance from signup answers 
        """
        analysis_prompt = f"""
        Based on these signup responses, analyze the user's profile and bucket them into one of four personality types.
        Create a detailed profile following these specific categories. Respond ONLY with a valid JSON object.
        
        Responses to analyze:
        {json.dumps(signup_answers, indent=2)}
        
        Required fields and their meanings:
        - name: Extract from responses
        - profession: {{
            category: job category,
            role: specific job title,
            experience_years: numeric years of experience,
            engagement_level: numeric 1-4 representing engagement level
        }}
        - personality: {{
            primary_bucket: one of [analyst, connector, commander, explorer],
            conversation_style: one of [structured, story_rich, direct, non_linear],
            response_style: one of [metrics, feelings, action, possibility],
            engagement_score: numeric 1-4 representing engagement intensity
        }}
        
        IMPORTANT: Ensure the response is a VALID JSON object that can be parsed directly.
        """


        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a psychological profiler specializing in the four personality buckets: analyst, connector, commander, and explorer. Always respond with a valid JSON object."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1
            )
            
            raw_content = response.choices[0].message.content
            logger.info(f"Raw : {raw_content}")
            
            try:
                # First try to remove any markdown code block formatting
                cleaned_content = re.sub(r'```(?:json)?\s*(.*?)\s*```', r'\1', raw_content, flags=re.DOTALL)
                logger.info(f"cleaned content : {cleaned_content}")
                profile_data = json.loads(cleaned_content)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON Parsing Error: {json_err}")
                
                # Try to extract JSON between curly braces if initial parse fails
                json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
                if json_match:
                    try:
                        profile_data = json.loads(json_match.group(0))
                    except Exception as extract_err:
                        logger.error(f"Failed to extract JSON: {extract_err}")
                        raise ValueError(f"Could not parse profile data: {cleaned_content}")
                else:
                    raise ValueError(f"No valid JSON found in response: {cleaned_content}")
            
            profile_data['user_id'] = user_id
            
            return cls(**profile_data)
            
        except Exception as e:
            logger.error(f"Detailed error creating user profile: {str(e)}")
            raise ValueError(f"Error creating user profile: {str(e)}")

    def to_dict(self) -> dict:
        """Convert profile to dictionary format"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "profession": {
                "category": self.profession.category,
                "role": self.profession.role,
                "experience_years": self.profession.experience_years,
                "engagement_level": self.profession.engagement_level.value
            },
            "personality": {
                "primary_bucket": self.personality.primary_bucket.value,
                "conversation_style": self.personality.conversation_style.value,
                "response_style": self.personality.response_style.value,
                "engagement_score": self.personality.engagement_score.value
            }
        }

app = FastAPI()

openai_client = AsyncOpenAI() 

@app.post("/builderprofile")
async def create_user_profile(request: ProfileRequest):
    """
    Endpoint to create a user profile from stored signup answers in Supabase
    """
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        logger.info(f"Fetching signup answers for user: {request.user_id}")
        
        # Remove .single() and handle multiple rows
        result = supabase.table('one_srswti_reverse_invited') \
            .select('signup_answers, email') \
            .eq('user_id', request.user_id) \
            .execute()
            
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="No data found for this user"
            )
        
        # Take the first row if multiple exist
        data = result.data[0]
        signup_answers = data.get('signup_answers')
        
        if not signup_answers:
            raise HTTPException(
                status_code=404,
                detail="No signup answers found for this user"
            )
        
        logger.info(f"Creating profile for user: {request.user_id}")
        
        profile = await UserProfile.from_signup_answers(
            user_id=request.user_id,
            signup_answers=signup_answers,
            openai_client=openai_client
        )
        
        try:
            profile_dict = profile.to_dict()
            supabase.table('one_srswti_reverse_invited') \
                .update({
                    'user_profile': profile_dict
                }) \
                .eq('user_id', request.user_id) \
                .execute()
            
            logger.info(f"Profile saved successfully for user: {request.user_id}")
            
        except Exception as save_error:
            logger.error(f"Error saving profile to Supabase: {str(save_error)}")
        
        return profile.to_dict()
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in create_user_profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8777)
