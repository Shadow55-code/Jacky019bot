import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️ python-dotenv not installed, using fallback values")

# Get tokens from environment variables with fallback to hardcoded values
Token = os.getenv('BOT_TOKEN', '7514819775:AAE3fyvXbDabvJQNPYwVm6CYnBl0k2A7T_U').strip()
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')

print(f"🔑 Using Bot Token: {Token[:20]}...")
print(f"🔑 Using Groq API Key: {GROQ_API_KEY[:20]}...")

bot = telebot.TeleBot(Token)

# Store user states
user_states = {}

# GROQ API details
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Request headers
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """🤖 Welcome to ShadowAI Bot!

Available commands:
/start - Show this message
/help - List of commands
/solutions - Get help solving a problem using LLaMA 3
/chess - Play chess online
/ludo - Play ludo online
""")

# /help command
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, """🛠️ Commands:
/start - Show welcome message
/help - List of commands
/solutions - Submit a problem to solve with AI
/chess - Play chess online
/ludo - Play ludo online
""")

# /solutions command
@bot.message_handler(commands=['solutions'])
def solutions(message):
    user_states[message.chat.id] = "awaiting_problem"
    bot.reply_to(message, "💭 Please enter your problem or question:")

# /chess command with inline button
@bot.message_handler(commands=['chess'])
def chess(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("♟️ Play Chess Online", url="https://lichess.org")
    markup.add(btn)
    bot.send_message(message.chat.id, "Click the button to play chess:", reply_markup=markup)

# /ludo command with inline button
@bot.message_handler(commands=['ludo'])
def ludo(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("🎲 Play Ludo Online", url="https://www.ludokings.com")
    markup.add(btn)
    bot.send_message(message.chat.id, "Click the button to play ludo:", reply_markup=markup)

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if user_states.get(user_id) == "awaiting_problem":
        problem = message.text
        bot.reply_to(message, "🤖 Solving your problem with LLaMA 3...")

        # Prepare request data
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": problem}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                # Limit response length for Telegram
                if len(answer) > 4000:
                    answer = answer[:4000] + "...\n\n(Response truncated due to length)"
                bot.send_message(user_id, f"💡 Solution:\n\n{answer}")
            else:
                bot.send_message(user_id, f"❌ Groq API error: {response.status_code}")
                print(f"API Error details: {response.text}")
        except Exception as e:
            bot.send_message(user_id, f"⚠️ Request error occurred. Please try again.")
            print(f"Error details: {str(e)}")

        user_states.pop(user_id, None)
    else:
        # Safer fallback - avoid eval()
        text = message.text.strip()
        if text.replace('.', '').replace('-', '').replace('+', '').replace('*', '').replace('/', '').replace('(', '').replace(')', '').replace(' ', '').isdigit() or any(op in text for op in ['+', '-', '*', '/']):
            try:
                # Simple math evaluation with limited scope
                allowed_chars = set('0123456789+-*/.() ')
                if all(c in allowed_chars for c in text):
                    result = eval(text)
                    bot.reply_to(message, f"🧮 Result: {result}")
                else:
                    bot.reply_to(message, "📋 Unrecognized input. Use /help to see available commands.")
            except:
                bot.reply_to(message, "❌ Invalid mathematical expression.")
        else:
            bot.reply_to(message, "📋 Unrecognized input. Use /help to see available commands.")

# Start the bot with error handling
if __name__ == "__main__":
    print("🤖 ShadowAI Bot is starting...")
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Bot crashed: {e}")