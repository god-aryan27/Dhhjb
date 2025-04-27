import telebot
from telebot import types
import time
import random
import json

# Bot Details
BOT_TOKEN = '8011013049:AAGVlTalTLZ-LI24aPflJM6Iptmb13W3Hvo'
bot = telebot.TeleBot(BOT_TOKEN)
CHANNEL_ID = -1002316557460  # Private channel ID
ADMIN_ID = 7401896933  # Admin ID
FORCE_JOIN_CHANNEL = 'https://t.me/+g-i8Vohdrv44NDRl'  # Force Join channel link
NON_FORCE_JOIN_CHANNEL = 'https://t.me/some_other_channel'  # Non-force join channel link

# Data Storage (for user information and session management)
users = {}

# Helper Functions
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def force_join_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Join Force Channel", url=FORCE_JOIN_CHANNEL))
    return markup

def non_force_join_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Join Non-Force Channel", url=NON_FORCE_JOIN_CHANNEL))
    return markup

def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Random Chat", "🎯 Filter Chat")
    markup.row("👤 Profile", "⚙️ Settings", "💰 Referral", "💎 Buy Points")
    return markup

def update_user_data():
    with open("users.json", "w") as file:
        json.dump(users, file)

def load_user_data():
    global users
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

def get_user_time_left(user_id):
    user = users.get(user_id)
    if user:
        remaining_time = user['session'] - time.time()
        if remaining_time < 0:
            return 0
        return remaining_time
    return 0

# Chat Partner and Time Management
def handle_chat_with_partner(user_id, partner_id):
    user = users[user_id]
    partner = users[partner_id]
    bot.send_message(user_id, f"Connected with {partner_id}. Say hi!")
    bot.send_message(partner_id, f"Connected with {user_id}. Say hi!")
    bot.send_message(user_id, "🔒 Use /disconnect to stop the chat.")
    bot.send_message(partner_id, "🔒 Use /disconnect to stop the chat.")
    
    user["partner"] = partner_id
    partner["partner"] = user_id

    update_user_data()

def disconnect_chat(user_id):
    user = users.get(user_id)
    if user:
        partner_id = user.get("partner")
        if partner_id:
            bot.send_message(partner_id, "The user has disconnected.")
            bot.send_message(user_id, "You have disconnected from the chat.")
            user["partner"] = None
            users[partner_id]["partner"] = None
            update_user_data()

# Command Handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {
            "gender": None,
            "age": None,
            "country": None,
            "filter_gender": None,
            "filter_age": None,
            "filter_country": None,
            "partner": None,
            "referrals": 0,
            "points": 0,
            "level": 1,
            "session": time.time() + 3600  # 1 Hour for new user
        }
        update_user_data()

    if not is_member(user_id):
        join_markup = force_join_menu()
        bot.send_message(user_id, "⚡ Please join our channel first!", reply_markup=join_markup)
        return

    bot.send_message(user_id, "👋 Welcome to Datingxrobot! You have 1 hour of free filter chat.", reply_markup=start_menu())

@bot.message_handler(commands=['forcejoin'])
def force_join(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        join_markup = force_join_menu()
        bot.send_message(user_id, "⚡ Please join the force join channel to proceed.", reply_markup=join_markup)
        return
    else:
        bot.send_message(user_id, "✅ You have joined the channel!", reply_markup=start_menu())

@bot.message_handler(commands=['nonforcejoin'])
def non_force_join(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f"📢 Please join the Non-Force Join Channel:\n{NON_FORCE_JOIN_CHANNEL}", reply_markup=non_force_join_menu())

# Main Flow (message handler)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main(message):
    user_id = message.from_user.id

    if user_id not in users:
        return start(message)

    if not is_member(user_id):
        join_markup = force_join_menu()
        bot.send_message(user_id, "⚡ Please join the force join channel first!", reply_markup=join_markup)
        return

    # Time left logic
    time_left = get_user_time_left(user_id)
    if time_left <= 0:
        bot.send_message(user_id, "⏳ Your free filter chat time is over. Refer 3 users for 2 extra hours.")
        return

    text = message.text
    if text == "🔍 Random Chat":
        bot.send_message(user_id, "⏳ Searching for a random partner...")
        partner_id = random.choice(list(users.keys()))
        bot.send_message(user_id, f"Found a match: {partner_id} 👫")
        handle_chat_with_partner(user_id, partner_id)

    elif text == "🎯 Filter Chat":
        bot.send_message(user_id, "⏳ Searching for a matching partner based on your filter...")
        filter_matches(user_id)

    elif text == "👤 Profile":
        user_profile = users[user_id]
        profile_info = f"👤 Your Profile:\nGender: {user_profile['gender']}\nAge: {user_profile['age']}\nCountry: {user_profile['country']}"
        bot.send_message(user_id, profile_info, reply_markup=start_menu())

    elif text == "⚙️ Settings":
        bot.send_message(user_id, "⚙️ Settings Menu:", reply_markup=start_menu())

    elif text == "💰 Referral":
        bot.send_message(user_id, "💬 Your Referral Link:\nhttps://t.me/Datingxrobot?start=" + str(user_id))

    elif text == "💎 Buy Points":
        bot.send_message(user_id, "🛍️ You can buy points here. 100 points = 1 USD.\nUse /exchange_points to see current points.")

    elif text == "💸 Exchange Points":
        bot.send_message(user_id, "💸 Current Points: " + str(users[user_id]["points"]))

def filter_matches(user_id):
    user = users[user_id]
    matches = []
    for other_user_id, other_user in users.items():
        if other_user_id != user_id and other_user['filter_gender'] == user['filter_gender']:
            if other_user['filter_age'] == user['filter_age'] and other_user['filter_country'] == user['filter_country']:
                matches.append(other_user_id)

    if matches:
        for match in matches:
            matched_user = users[match]
            match_info = f"🎯 Match Found!\nGender: {matched_user['gender']}\nAge: {matched_user['age']}\nCountry: {matched_user['country']}"
            bot.send_message(user_id, match_info)
    else:
        bot.send_message(user_id, "No matches found based on your filters.")

# Chatting System (Random Chat)
@bot.message_handler(commands=['chat'])
def chat(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(user_id, "👋 Please complete your profile first!")
        return

    if not is_member(user_id):
        join_markup = force_join_menu()
        bot.send_message(user_id, "⚡ Please join the channel to start chatting.", reply_markup=join_markup)
        return
    
    # Random chat
    partner_id = random.choice(list(users.keys()))
    if partner_id != user_id:
        bot.send_message(user_id, f"Connecting with user {partner_id}...")
        bot.send_message(partner_id, f"New chat request from {user_id}. Say hi!")
        handle_chat_with_partner(user_id, partner_id)

# Disconnect Command
@bot.message_handler(commands=['disconnect'])
def disconnect(message):
    user_id = message.from_user.id
    disconnect_chat(user_id)

# Admin Commands (for administrative control)
@bot.message_handler(commands=['admin'])
def admin_controls(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Admin Menu:", reply_markup=start_menu())
    else:
        bot.send_message(message.chat.id, "You are not authorized.")

# Main Callback Query Handler
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "set_gender":
        bot.send_message(user_id, "🚻 Choose your gender:")
    elif call.data == "set_age":
        bot.send_message(user_id, "🎂 Choose your age:")
    elif call.data == "set_country":
        bot.send_message(user_id, "🌎 Choose your country:")
    elif call.data == "reset_settings":
        users[user_id]["filter_gender"] = None
        users[user_id]["filter_age"] = None
        users[user_id]["filter_country"] = None
        update_user_data()
        bot.send_message(user_id, "✅ Filter settings reset!")

# Start the bot
if __name__ == "__main__":
    load_user_data()
    bot.polling(none_stop=True)
