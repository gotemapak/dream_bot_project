import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DreamAnalytics:
    def __init__(self):
        self.analytics_dir = Path("analytics")
        self.analytics_dir.mkdir(exist_ok=True)
        self.daily_file = self.analytics_dir / f"dream_analytics_{datetime.now().strftime('%Y_%m')}.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create analytics file if it doesn't exist"""
        if not self.daily_file.exists():
            initial_data = {
                "total_dreams": 0,
                "voice_messages": 0,
                "text_messages": 0,
                "errors": 0,
                "tokens_used": 0,
                "common_themes": {},
                "user_interactions": {},
                "daily_stats": {}
            }
            self._save_data(initial_data)

    def _load_data(self):
        """Load analytics data from file"""
        try:
            with open(self.daily_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            return None

    def _save_data(self, data):
        """Save analytics data to file"""
        try:
            with open(self.daily_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")

    def get_user_monthly_usage(self, user_id: int) -> dict:
        """Get user's usage statistics for current month"""
        data = self._load_data()
        if not data or str(user_id) not in data['user_interactions']:
            return {"total_dreams": 0, "voice_messages": 0, "text_messages": 0}
        
        user_data = data['user_interactions'][str(user_id)]
        return {
            "total_dreams": user_data.get('total_dreams', 0),
            "voice_messages": user_data.get('voice_messages', 0),
            "text_messages": user_data.get('text_messages', 0)
        }

    def check_monthly_limit(self, user_id: int, message_type: str) -> bool:
        """Check if user has reached monthly limit"""
        usage = self.get_user_monthly_usage(user_id)
        
        # Monthly limit of 20 messages (combined voice and text)
        monthly_limit = 20
        
        return usage["total_dreams"] < monthly_limit

    def log_dream_interpretation(self, user_id: int, message_type: str, dream_text: str, tokens_used: int):
        """Log a dream interpretation interaction"""
        data = self._load_data()
        if not data:
            return

        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update total counts
        data['total_dreams'] += 1
        data[f'{message_type}_messages'] += 1
        data['tokens_used'] += tokens_used

        # Update user statistics
        if str(user_id) not in data['user_interactions']:
            data['user_interactions'][str(user_id)] = {
                'total_dreams': 0,
                'voice_messages': 0,
                'text_messages': 0,
                'first_interaction': today,
                'last_interaction': today
            }
        
        user_data = data['user_interactions'][str(user_id)]
        user_data['total_dreams'] += 1
        user_data[f'{message_type}_messages'] = user_data.get(f'{message_type}_messages', 0) + 1
        user_data['last_interaction'] = today

        # Update daily statistics
        if today not in data['daily_stats']:
            data['daily_stats'][today] = {
                'total_dreams': 0,
                'voice_messages': 0,
                'text_messages': 0,
                'tokens_used': 0
            }
        
        data['daily_stats'][today]['total_dreams'] += 1
        data['daily_stats'][today][f'{message_type}_messages'] += 1
        data['daily_stats'][today]['tokens_used'] += tokens_used

        self._save_data(data)

    def log_error(self, error_type: str, error_message: str):
        """Log an error occurrence"""
        data = self._load_data()
        if not data:
            return

        data['errors'] += 1
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in data['daily_stats']:
            data['daily_stats'][today] = {
                'total_dreams': 0,
                'voice_messages': 0,
                'text_messages': 0,
                'tokens_used': 0,
                'errors': 0
            }
        
        if 'errors' not in data['daily_stats'][today]:
            data['daily_stats'][today]['errors'] = 0
            
        data['daily_stats'][today]['errors'] += 1

        self._save_data(data)

    def get_monthly_stats(self):
        """Get current month's statistics"""
        data = self._load_data()
        if not data:
            return None

        return {
            'total_dreams': data['total_dreams'],
            'voice_messages': data['voice_messages'],
            'text_messages': data['text_messages'],
            'total_users': len(data['user_interactions']),
            'tokens_used': data['tokens_used'],
            'errors': data['errors']
        }

    def get_daily_stats(self, date: str = None):
        """Get statistics for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        data = self._load_data()
        if not data or date not in data['daily_stats']:
            return None

        return data['daily_stats'][date] 