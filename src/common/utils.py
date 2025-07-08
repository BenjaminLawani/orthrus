import json
from typing import (
    Optional,
    Dict,
    Any,
    List
)
from sqlalchemy import text
from fastapi_mail import (
    MessageSchema,
    ConnectionConfig,
    FastMail
)
from groq import Client

from .database import SessionLocal
from .config import settings

groq_client = Client(api_key=settings.GROQ_API_KEY)

def get_user_interests(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user interests from PostgreSQL database"""
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT interests FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        session.close()

def get_potential_matches(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get potential matches excluding the current user"""
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT user_id, interests FROM users WHERE user_id != :user_id LIMIT :limit"),
            {"user_id": user_id, "limit": limit}
        ).fetchall()
        return [{"user_id": str(row[0]), "interests": row[1]} for row in result]
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        session.close()

def analyze_compatibility(user1_interests: Dict, user2_interests: Dict) -> Dict[str, Any]:
    """Use Groq LLM to analyze compatibility between two users"""
    
    prompt = f"""
    You are a sophisticated matching algorithm. Analyze the compatibility between two users based on their interests.

    User 1 interests: {json.dumps(user1_interests, indent=2)}
    User 2 interests: {json.dumps(user2_interests, indent=2)}

    Please provide:
    1. A compatibility score between 0.0 and 1.0 (where 1.0 is perfect match)
    2. Exactly 3 sentences explaining the rationale behind this score

    Consider factors like:
    - Shared interests and hobbies
    - Complementary interests that could work well together
    - Lifestyle compatibility
    - Values alignment
    - Potential for meaningful connection

    Return your response in the following JSON format:
    {{
        "compatibility_score": <float between 0.0 and 1.0>,
        "rationale": "<exactly 3 sentences explaining the match>"
    }}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert relationship compatibility analyzer. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "compatibility_score": float(result["compatibility_score"]),
            "rationale": result["rationale"]
        }
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return {
            "compatibility_score": 0.0,
            "rationale": "Unable to analyze compatibility due to system error. Please try again later."
        }

def find_matches(user_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """Find top matches for a given user"""
    
    user_interests = get_user_interests(user_id)
    if not user_interests:
        return []
    
    potential_matches = get_potential_matches(user_id)
    if not potential_matches:
        return []
    
    matches = []
    
    for candidate in potential_matches:
        try:
            compatibility = analyze_compatibility(user_interests, candidate['interests'])
            
            matches.append({
                "user_id": candidate['user_id'],
                "compatibility_score": compatibility['compatibility_score'],
                "rationale": compatibility['rationale']
            })
            
        except Exception as e:
            print(f"Error analyzing match for {candidate['user_id']}: {e}")
            continue
    
    # Sort by compatibility score and return top N
    matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
    return matches[:top_n]

def single_match_analysis(user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
    """Analyze compatibility between two specific users"""
    
    user1_interests = get_user_interests(user1_id)
    user2_interests = get_user_interests(user2_id)
    
    if not user1_interests or not user2_interests:
        return None
    
    compatibility = analyze_compatibility(user1_interests, user2_interests)
    
    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "compatibility_score": compatibility['compatibility_score'],
        "rationale": compatibility['rationale']
    }

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM="la.benjamib@gmail.com",
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fast_mail = FastMail(self.conf)

    async def send_email(self, subject: str, recipients: list, body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html"
        )
        await self.fast_mail.send_message(message)

fm = EmailService()