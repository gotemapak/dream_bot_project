# Dream Interpreter Telegram Bot

A Telegram bot that interprets dreams using AI. Users can submit their dreams via text or voice messages, and receive insightful interpretations powered by OpenAI's GPT and Whisper APIs.

## Features

- 🗣 Voice message support with automatic transcription
- ✍️ Text message support
- 🤖 AI-powered dream interpretation
- 🎯 Clear and insightful responses
- 💬 Interactive follow-up questions

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- An OpenAI API key
- PostgreSQL database (optional)

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd dream-bot-project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your credentials:
- Add your Telegram Bot Token
- Add your OpenAI API key
- Configure database URL if needed

## Running the Bot

1. Make sure your virtual environment is activated
2. Run the bot:
```bash
python bot.py
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to get the welcome message
3. Send your dream either as:
   - A text message
   - A voice message
4. Wait for the interpretation
5. Ask follow-up questions if needed

## Error Handling

The bot includes error handling for:
- Voice message processing issues
- API failures
- Connection problems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 