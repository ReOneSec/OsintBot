# LeakOsint Telegram Bot

A powerful, robust Python-based Telegram bot that acts as a front-end for the LeakOsint API. It allows users to query for information in data leaks directly from their Telegram client, with results presented in a clean, interactive, and paginated format.

## Features

- **Seamless API Integration**: Securely queries the LeakOsint API for data based on user input.
- **Interactive UI**: Uses Telegram's inline keyboards to provide a rich user experience with page navigation (`<<` and `>>`) and a 🗑️ Delete button.
- **Advanced Caching**: Implements a Time-To-Live (TTL) cache to store recent results, reducing API spam and speeding up repeat queries while preventing long-term memory leaks.
- **Rate Limiting**: Includes a user-side cooldown mechanism to prevent spam and protect the backend API from abuse.
- **Secure Configuration**: Manages all sensitive credentials (bot and API tokens) and settings via an external `config.ini` file, keeping secrets out of the source code.
- **Comprehensive Logging**: Logs all important events, API responses, and errors to a `bot.log` file for easy debugging and monitoring.
- **User-Friendly Commands**: Features standard `/start` and `/help` commands for easy onboarding.
- **Graceful Error Handling**: Intelligently handles non-text messages, API errors, and network issues, providing clear feedback to the user.

## Demo

A user sends a query (e.g., an email address) to the bot. The bot replies with the findings, grouped by the source of the data leak.

**User sends a message**: `example@email.com`

**Bot replies**:

⏳ Searching, please wait...
(This message is deleted and replaced with the result)
```

```
[ Photo ] [ Video ]
<b>breach_database_1</b>

InfoLeak: A major breach from a popular social media site in 2021.

<b>email</b>: example@email.com
<b>username</b>: example_user
<b>password_hash</b>: $2a$10$...

[ << ]   [ 1/5 ]   [ >> ]
[      🗑️ Delete      ]
```

## Setup and Installation

Follow these steps to get your own instance of the bot running.

### 1. Prerequisites

- Python 3.8 or newer.
- `pip` for installing packages.

### 2. Clone the Repository

Clone this project to your local machine or server.

```bash
git clone <your-repository-url>
cd <repository-folder>
```

### 3. Create Project Files

You will need three main files in your project directory: `bot.py`, `config.ini`, and `requirements.txt`.

#### `requirements.txt`

Create this file and add the following dependencies:

```
pyTelegramBotAPI
requests
cachetools
```

#### `config.ini`

Create this file to store your secret tokens and settings. **Never share this file or commit it to a public repository.**

```ini
[TELEGRAM]
; Get this from @BotFather on Telegram
BOT_TOKEN = YOUR_TELEGRAM_BOT_TOKEN_HERE

[API]
; Get this from the LeakOsint service
API_TOKEN = YOUR_LEAKOSINT_API_TOKEN_HERE
API_URL = https://leakosint.api/
```

#### `bot.py`

This is where you will place the main Python script for the bot.

### 4. Install Dependencies

Install all the required Python libraries using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Run the Bot

Start the bot with the following command. The bot will start polling for new messages and log its activity to `bot.log`.

```bash
python bot.py
```

To keep the bot running in the background on a server, you can use tools like `screen` or `systemd`.

## Usage

Once the bot is running, you can interact with it on Telegram:

- **Start a chat**: Find your bot on Telegram and send the `/start` command.
- **Get help**: Send `/help` to see usage instructions.
- **Send a query**: Send any text message containing an email, phone number, or username you want to investigate.
- **Navigate results**: Use the `<<` and `>>` buttons to browse through different pages of the report.
- **Clean up**: Use the 🗑️ Delete button to remove the report from your chat.

## Technologies Used

- **Python**: Core programming language.
- **pyTelegramBotAPI**: A simple and feature-rich library for the Telegram Bot API.
- **Requests**: For making HTTP requests to the Telegram API.
- **cachetools**: For implementing the Telegram API-memory TTL cache.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
```
