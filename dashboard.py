from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyQuery
from pathlib import Path
import os
import logging
from datetime import datetime, timedelta
from analytics import DreamAnalytics
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug: Print environment variables
dashboard_token = os.getenv('DASHBOARD_TOKEN')
logger.debug(f"Loaded DASHBOARD_TOKEN: {dashboard_token}")

app = FastAPI(title="Dream Bot Analytics Dashboard")
analytics = DreamAnalytics()

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Security
api_key_query = APIKeyQuery(name="token", auto_error=False)

async def verify_token(token: str = Depends(api_key_query)):
    """Verify the dashboard access token"""
    logger.debug(f"Received token: {token}")
    logger.debug(f"Expected token: {os.getenv('DASHBOARD_TOKEN')}")
    
    if not token:
        logger.warning("No token provided")
        raise HTTPException(
            status_code=401,
            detail="Необходим токен доступа для просмотра статистики",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token != os.getenv('DASHBOARD_TOKEN'):
        logger.warning(f"Invalid token provided: {token}")
        raise HTTPException(
            status_code=401,
            detail="Неверный токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug("Token verification successful")
    return token

@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    token: str = Depends(verify_token)
):
    """Display the main dashboard"""
    # Get current month's stats
    monthly_stats = analytics.get_monthly_stats()
    if not monthly_stats:
        monthly_stats = {
            'total_dreams': 0,
            'voice_messages': 0,
            'text_messages': 0,
            'total_users': 0,
            'tokens_used': 0,
            'errors': 0
        }

    # Get daily stats for the last 7 days
    daily_stats = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        stats = analytics.get_daily_stats(date)
        if stats:
            stats['date'] = date
            daily_stats.append(stats)

    # Calculate some derived metrics
    if monthly_stats['total_dreams'] > 0:
        voice_percentage = (monthly_stats['voice_messages'] / monthly_stats['total_dreams']) * 100
        text_percentage = (monthly_stats['text_messages'] / monthly_stats['total_dreams']) * 100
        avg_tokens_per_dream = monthly_stats['tokens_used'] / monthly_stats['total_dreams']
        error_rate = (monthly_stats['errors'] / monthly_stats['total_dreams']) * 100
    else:
        voice_percentage = 0
        text_percentage = 0
        avg_tokens_per_dream = 0
        error_rate = 0

    # Calculate estimated costs (assuming current OpenAI pricing)
    gpt4_cost_per_1k = 0.03  # $0.03 per 1K tokens
    whisper_cost_per_minute = 0.006  # $0.006 per minute
    estimated_voice_minutes = monthly_stats['voice_messages'] * 2  # Assuming average 2 minutes per voice message
    
    gpt4_cost = (monthly_stats['tokens_used'] / 1000) * gpt4_cost_per_1k
    whisper_cost = estimated_voice_minutes * whisper_cost_per_minute
    total_cost = gpt4_cost + whisper_cost

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "monthly_stats": monthly_stats,
            "daily_stats": daily_stats,
            "voice_percentage": round(voice_percentage, 1),
            "text_percentage": round(text_percentage, 1),
            "avg_tokens_per_dream": round(avg_tokens_per_dream, 1),
            "error_rate": round(error_rate, 1),
            "current_month": datetime.now().strftime('%B %Y'),
            "estimated_cost": round(total_cost, 2)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 