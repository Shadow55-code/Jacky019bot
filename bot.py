import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Your Bot Token from BotFather
Token = "7514819775:AAE3fyvXbDabvJQNPYwVm6CYnBl0k2A7T_U".strip()
bot = telebot.TeleBot(Token)

# Delete existing webhook to avoid polling conflict
bot.remove_webhook()

# Store user states
user_states = {}

# GROQ API details
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"  # Replace with your real Groq API key

# Request headers
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """Welcome to ShadowAI Bot!

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
    bot.reply_to(message, "Please enter your problem or question:")

# /chess command with inline button
@bot.message_handler(commands=['chess'])
def chess(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Play Chess Online", url="https://lichess.org")
    markup.add(btn)
    bot.send_message(message.chat.id, "Click the button to play chess:", reply_markup=markup)

# /ludo command with inline button
@bot.message_handler(commands=['ludo'])
def ludo(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Play Ludo Online", url="https://www.ludokings.com")
    markup.add(btn)
    bot.send_message(message.chat.id, "Click the button to play ludo:", reply_markup=markup)

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if user_states.get(user_id) == "awaiting_problem":
        problem = message.text
        bot.reply_to(message, "Solving your problem with LLaMA 3...")

        # Prepare request data
        data = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": problem}],
            "temperature": 0.7
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                bot.send_message(user_id, f"Solution:\n{answer}")
            else:
                bot.send_message(user_id, f"Groq API error: {response.status_code}\n{response.text}")
        except Exception as e:
            bot.send_message(user_id, f"⚠️ Request error: {str(e)}")

        user_states.pop(user_id, None)
    else:
        try:
            result = eval(message.text.strip())
            bot.reply_to(message, f"Result: {result}")
        except:
            bot.reply_to(message, "Unrecognized input. Use /help to see available commands.")

# Start the bot
print("Bot is running...")
bot.infinity_polling()
