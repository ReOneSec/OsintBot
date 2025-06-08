```markdown
# LeakOsint Telegram Bot

A powerful, robust Python-based Telegram bot that acts as a front-end for the LeakOsint API. It allows users to query for information in data leaks directly from their Telegram client, with results presented in a clean, interactive, and paginated format.

## Features
- **Seamless API Integration**: Securely queries the LeakOsint API for data based on user input
- **Interactive UI**: Uses Telegram's inline keyboards for page navigation (`<<` and `>>`) and includes a 🗑️ Delete button
- **Advanced Caching**: Implements TTL cache to reduce API spam and prevent memory leaks
- **Rate Limiting**: User-side cooldown mechanism to prevent abuse
- **Secure Configuration**: Manages secrets via external `config.ini` file
- **Comprehensive Logging**: Logs events to `bot.log` for monitoring
- **User-Friendly Commands**: `/start` and `/help` for onboarding
- **Graceful Error Handling**: Handles non-text messages, API errors, and network issues

## Demo
**User query**:  
`example@email.com`  

**Bot response**:  
⏳ *Searching, please wait...* (deleted after result)  

**Result format**:  
```
---
[ Photo ] [ Video ]
**breach_database_1**

InfoLeak: A major breach from a popular social media site in 2021.

**email**: example@email.com
**username**: example_user
**password_hash**: $2a$10$...

[ << ]   [ 1/5 ]   [ >> ]
[      🗑️ Delete      ]
```

## Setup and Installation

### 1. Prerequisites
- Python 3.8+
- `pip` package manager

### 2. Clone Repository
```bash
git clone <your-repository-url>
cd <repository-folder>
```

### 3. Create Project Files
**`requirements.txt`**:
```
pyTelegramBotAPI
requests
cachetools
```

**`config.ini`** (Never commit this!):
```ini
[TELEGRAM]
# Get from @BotFather
BOT_TOKEN = YOUR_TELEGRAM_BOT_TOKEN_HERE

[LEAKOSINT]
# Get from LeakOsint service
API_TOKEN = YOUR_LEAKOSINT_API_TOKEN_HERE
API_URL = https://leakosintapi.com/
LANG = ru
LIMIT = 300
```

**`bot.py`** (Main script - [see source code](https://github.com/yourusername/leakosint-telegram-bot))

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Bot
```bash
python bot.py
```
> **Tip**: Use `screen` or `systemd` for background operation

## Usage
1. **Start**: Send `/start` in Telegram
2. **Help**: Send `/help` for instructions
3. **Query**: Send email/phone/username to investigate
4. **Navigate**: Use `<<`/`>>` buttons to browse pages
5. **Clean**: Click 🗑️ Delete to remove results

## Technologies Used
- **Python**: Core programming language
- **pyTelegramBotAPI**: Telegram bot framework
- **Requests**: HTTP API interactions
- **cachetools**: In-memory TTL caching

## License
MIT License - See [LICENSE](LICENSE) for details
```
