# Dreamy - AI Dream Interpretation Bot 🌙✨

A Telegram bot that helps interpret dreams using artificial intelligence. Users can submit their dreams via text or voice messages and receive deep interpretations based on psychology and symbolism.

## Key Features

- 🗣 Voice message support with automatic transcription
- ✍️ Text message support for dream descriptions
- 🤖 Dream interpretation powered by GPT-4
- 🎯 Clear and insightful interpretations
- 💬 Interactive follow-up questions and dialogue
- 📖 Dream history with preview functionality
- 📊 Usage statistics
- 🔄 Monthly limit of 20 dreams

## Technical Requirements

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API key
- FastAPI for analytics dashboard (optional)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:gotemapak/dream_bot_project.git
cd dream_bot_project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file and add necessary environment variables:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DASHBOARD_TOKEN=your_dashboard_token
```

## Running the Bot

1. Ensure your virtual environment is activated
2. Run the bot:
```bash
python bot.py
```

## Usage

1. Start a chat with the bot on Telegram
2. Send `/start` to get the welcome message
3. Submit your dream in one of two ways:
   - As a text message
   - As a voice message
4. Wait for the interpretation
5. Use the menu buttons to:
   - View dream history
   - Check statistics
   - Ask follow-up questions

## Analytics Dashboard

To run the analytics dashboard:
```bash
python dashboard.py
```
The dashboard will be available at: `http://localhost:8000?token=your_dashboard_token`

## Error Handling

The bot includes handling for:
- Voice message processing issues
- API errors
- Connection problems
- Monthly limit exceeded

## System Architecture

The bot utilizes several key technologies:
- OpenAI Whisper API for voice-to-text conversion
- OpenAI GPT-4 for dream interpretation
- FastAPI for the analytics dashboard
- JSON-based storage for dream history and analytics

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 