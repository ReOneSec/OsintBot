import telebot
import requests
import logging
import configparser
import time
from random import randint
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from cachetools import TTLCache

# --- CONFIGURATION AND LOGGING SETUP ---

# Load configuration from config.ini
config = configparser.ConfigParser()
try:
    config.read_file(open('config.ini'))
except FileNotFoundError:
    print("FATAL: config.ini not found. Please create it. Exiting.")
    exit()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- BOT AND API CREDENTIALS ---
try:
    BOT_TOKEN = config['TELEGRAM']['BOT_TOKEN']
    API_TOKEN = config['LEAKOSINT']['API_TOKEN']
    API_URL = config['LEAKOSINT']['API_URL']
    LANG = config['LEAKOSINT'].get('LANG', 'ru')
    LIMIT = config['LEAKOSINT'].getint('LIMIT', 300)
except KeyError as e:
    logger.fatal(f"Missing required configuration key in config.ini: {e}")
    exit()

# --- CONSTANTS AND GLOBAL VARIABLES ---
CALLBACK_PREFIX_PAGE = "/page "
CALLBACK_DELETE = "/delete"
MAX_MESSAGE_LENGTH = 4096
USER_COOLDOWN = 3  # Seconds a user must wait between queries

# Use a Time-To-Live cache for reports: max 500 reports, each lasts 1 hour (3600s)
cash_reports = TTLCache(maxsize=500, ttl=3600)
# Dictionary to track user message timestamps for rate limiting
user_timestamps = {}
bot = telebot.TeleBot(BOT_TOKEN)

# --- HELPER FUNCTIONS ---

def generate_report(query: str, query_id: int) -> tuple[list | None, str | None]:
    """Generates a report by querying the LeakOsint API."""
    data = {"token": API_TOKEN, "request": query.split("\n")[0], "limit": LIMIT, "lang": LANG}
    try:
        response = requests.post(API_URL, json=data, timeout=30)
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while querying API: {e}")
        return None, "A network error occurred while contacting the search service."
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Failed to decode JSON from API. Response text: {response.text}")
        return None, "The search service returned an invalid response. Please try again later."

    logger.info(f"API Response for query '{query}': {response_json}")

    if "Error code" in response_json:
        error_detail = response_json.get("Error detail", "No detail provided.")
        return None, f"An API error occurred: {error_detail}"

    if not response_json.get("List"):
        return [], None

    report_pages = []
    for database_name, details in response_json["List"].items():
        text_parts = [f"<b>{database_name}</b>", ""]
        text_parts.append(details.get("InfoLeak", "") + "\n")
        if "Data" in details:
            for report_data in details["Data"]:
                for column_name, value in report_data.items():
                    text_parts.append(f"<b>{column_name}</b>:  {value}")
                text_parts.append("")
        full_text = "\n".join(text_parts)
        if len(full_text) > MAX_MESSAGE_LENGTH:
            full_text = full_text[:MAX_MESSAGE_LENGTH - 100] + "\n\n[...Message truncated...]"
        report_pages.append(full_text)

    if report_pages:
        cash_reports[str(query_id)] = report_pages
    return report_pages, None

def create_inline_keyboard(query_id: int, page_id: int, count_page: int) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for navigating and managing the report."""
    markup = InlineKeyboardMarkup()
    nav_buttons = []
    if count_page > 1:
        prev_page = page_id - 1 if page_id > 0 else count_page - 1
        next_page = page_id + 1 if page_id < count_page - 1 else 0
        nav_buttons = [
            InlineKeyboardButton(text="<<", callback_data=f"{CALLBACK_PREFIX_PAGE}{query_id} {prev_page}"),
            InlineKeyboardButton(text=f"{page_id + 1}/{count_page}", callback_data="no_action"),
            InlineKeyboardButton(text=">>", callback_data=f"{CALLBACK_PREFIX_PAGE}{query_id} {next_page}")
        ]
        markup.row(*nav_buttons)

    markup.row(InlineKeyboardButton(text="🗑️ Delete", callback_data=CALLBACK_DELETE))
    return markup

# --- TELEGRAM BOT HANDLERS ---

@bot.message_handler(commands=["start"])
def send_welcome(message: Message):
    """Handles the /start command with a brief welcome."""
    bot.reply_to(message, "Hi! I'm a bot for searching public databases. For more info on how to use me, send /help.")

@bot.message_handler(commands=["help"])
def send_help(message: Message):
    """Handles the /help command with detailed instructions."""
    help_text = (
        "<b>How to use this bot:</b>\n\n"
        "Simply send me a query to search for, such as:\n"
        "- An email address (<code>example@gmail.com</code>)\n"
        "- A phone number (<code>1234567890</code>)\n"
        "- A username (<code>example_user</code>)\n\n"
        "The bot will search for matches in public data leaks. You can navigate the results using the `<<` and `>>` buttons and delete the report with the `🗑️` button."
    )
    bot.reply_to(message, help_text, parse_mode="html")
    
    
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def handle_non_text(message: Message):
    """Responds to any non-text message."""
    bot.reply_to(message, "Sorry, I can only process text queries. Please send something like an email, phone number, or username.")


@bot.message_handler(content_types=["text"])
def handle_message(message: Message):
    """Handles all incoming text messages, with rate limiting."""
    user_id = message.from_user.id
    current_time = time.time()

    # Rate Limiting Check
    if user_id in user_timestamps and (current_time - user_timestamps[user_id]) < USER_COOLDOWN:
        bot.reply_to(message, f"Please wait {USER_COOLDOWN} seconds before sending another query.")
        return
    user_timestamps[user_id] = current_time

    query_id = randint(0, 9_999_999)
    logger.info(f"Received query '{message.text}' from user {user_id} ({message.from_user.username})")
    
    wait_message = bot.reply_to(message, "⏳ Searching, please wait...")
    report_pages, error = generate_report(message.text, query_id)
    bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)

    if error:
        bot.reply_to(message, f"⚠️ Error: {error}")
        return
    if not report_pages:
        bot.reply_to(message, "✅ No results found for your query.")
        return

    markup = create_inline_keyboard(query_id, 0, len(report_pages))
    try:
        bot.send_message(message.chat.id, report_pages[0], parse_mode="html", reply_markup=markup)
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Telegram API error on send: {e}. Falling back to plain text.")
        plain_text = report_pages[0].replace("<b>", "").replace("</b>", "")
        bot.send_message(message.chat.id, text=plain_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    """Handles all callback queries from inline buttons."""
    # Handle Page Navigation
    if call.data.startswith(CALLBACK_PREFIX_PAGE):
        try:
            _, query_id_str, page_id_str = call.data.split(" ")
            page_id = int(page_id_str)
        except (ValueError, IndexError):
            bot.answer_callback_query(call.id, "Invalid callback data.")
            return

        if query_id_str not in cash_reports:
            bot.edit_message_text("This query has expired and its results are no longer available.",
                                  chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            bot.answer_callback_query(call.id, "Query expired.")
            return

        report_pages = cash_reports[query_id_str]
        markup = create_inline_keyboard(query_id_str, page_id, len(report_pages))
        try:
            bot.edit_message_text(report_pages[page_id], chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, parse_mode="html", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"Failed to edit message, might be identical: {e}")
        bot.answer_callback_query(call.id)

    # Handle Delete Button
    elif call.data == CALLBACK_DELETE:
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.answer_callback_query(call.id, "Report deleted.")
        except telebot.apihelper.ApiTelegramException as e:
            bot.answer_callback_query(call.id, "Could not delete message (it might be too old).")
            logger.error(f"Could not delete message: {e}")

    # Handle dummy buttons
    elif call.data == "no_action":
        bot.answer_callback_query(call.id)

if __name__ == '__main__':
    logger.info("Bot starting...")
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            logger.critical(f"An unhandled exception occurred in the polling loop: {e}", exc_info=True)
            time.sleep(5)
      
