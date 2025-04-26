import telebot
from telebot import types
import time
import random

# Config
TOKEN = "8011013049:AAGVlTalTLZ-LI24aPflJM6Iptmb13W3Hvo"
CHANNEL_ID = -1002316557460
ADMIN_ID = 7401896933
BOT_USERNAME = "Datingxrobot"

bot = telebot.TeleBot(TOKEN)

# Storage
users = {}
searching = []
filter_searching = []
chats = {}
referrals = {}
blocked_users = {}

# Force join
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_join_message(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Join Channel", url="https://t.me/+g-i8Vohdrv44NDRl"))
    markup.add(types.InlineKeyboardButton("✅ Joined", callback_data="joined"))
    bot.send_message(chat_id, "❗️ Please join our channel to use the bot!", reply_markup=markup)

# Helper
def check_force_join(message):
    if not is_user_in_channel(message.from_user.id):
        send_join_message(message.chat.id)
        return False
    if message.from_user.id in blocked_users and time.time() < blocked_users[message.from_user.id]:
        bot.send_message(message.chat.id, "🚫 You are blocked temporarily.")
        return False
    return True

def get_profile_text(user_id):
    data = users.get(user_id, {})
    gender = data.get("gender", "Not Set")
    age = data.get("age", "Not Set")
    country = data.get("country", "Not Set")
    refs = referrals.get(user_id, 0)
    points = data.get("points", 0)
    return f"👤 Profile\n\nGender: {gender}\nAge: {age}\nCountry: {country}\nReferrals: {refs}\nPoints: {points}"

# Start
@bot.message_handler(commands=['start'])
def start(message):
    if not check_force_join(message):
        return

    args = message.text.split()
    if len(args) > 1:
        code = args[1]
        if code.isdigit():
            ref_id = int(code)
            if ref_id != message.from_user.id:
                referrals[ref_id] = referrals.get(ref_id, 0) + 1
                users[ref_id]["points"] = users.get(ref_id, {}).get("points", 0) + 2
                bot.send_message(ref_id, f"🎉 New Referral! Total referrals: {referrals[ref_id]}")
                bot.send_message(ADMIN_ID, f"🆕 New Referral!\nUser: {ref_id}\nBy: {message.from_user.id}")

    bot.send_message(message.chat.id, f"👋 Welcome {message.from_user.first_name}!\nUse /profile to setup your profile.\n/start your dating journey!")

# Joined Callback
@bot.callback_query_handler(func=lambda call: call.data == "joined")
def joined(call):
    if is_user_in_channel(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ You have joined successfully!")
        bot.send_message(call.message.chat.id, "✅ Now use /profile to setup and /search to find partner!")
    else:
        bot.answer_callback_query(call.id, "❗️ Please join the channel first!")

# Profile
@bot.message_handler(commands=['profile'])
def profile(message):
    if not check_force_join(message):
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♂️ Male", callback_data="gender_Male"),
               types.InlineKeyboardButton("♀️ Female", callback_data="gender_Female"))
    markup.add(types.InlineKeyboardButton("🌏 Set Country", callback_data="set_country"))
    markup.add(types.InlineKeyboardButton("🎂 Set Age", callback_data="set_age"))
    bot.send_message(message.chat.id, get_profile_text(message.from_user.id), reply_markup=markup)

# Settings
@bot.message_handler(commands=['settings'])
def settings(message):
    if not check_force_join(message):
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Reset Settings", callback_data="reset_settings"))
    bot.send_message(message.chat.id, "⚙️ Settings:", reply_markup=markup)

# Set Gender
@bot.callback_query_handler(func=lambda call: call.data.startswith("gender_"))
def set_gender(call):
    gender = call.data.split("_")[1]
    users.setdefault(call.from_user.id, {})["gender"] = gender
    bot.answer_callback_query(call.id, f"✅ Gender set to {gender}")
    bot.edit_message_text(get_profile_text(call.from_user.id), call.message.chat.id, call.message.message_id)

# Set Country and Age
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_country"))
def ask_country(call):
    markup = types.InlineKeyboardMarkup()
    countries = ["🇮🇳 India", "🇰🇷 Korea", "🇷🇺 Russia", "🇱🇰 Sri Lanka", "🇮🇩 Indonesia"]
    for country in countries:
        markup.add(types.InlineKeyboardButton(country, callback_data=f"country_{country}"))
    bot.edit_message_text("🌏 Choose your Country:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def save_country(call):
    country = call.data.split("_", 1)[1]
    users.setdefault(call.from_user.id, {})["country"] = country
    bot.answer_callback_query(call.id, f"✅ Country set to {country}")
    bot.edit_message_text(get_profile_text(call.from_user.id), call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_age"))
def ask_age(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🎂 Send your Age (e.g., 18)")

@bot.message_handler(func=lambda message: message.text.isdigit() and 10 <= int(message.text) <= 99)
def save_age(message):
    users.setdefault(message.from_user.id, {})["age"] = message.text
    bot.send_message(message.chat.id, "✅ Age saved successfully!")

@bot.callback_query_handler(func=lambda call: call.data == "reset_settings")
def reset_settings(call):
    users[call.from_user.id] = {}
    bot.answer_callback_query(call.id, "🔄 Settings Reset!")
    bot.edit_message_text("✅ Settings have been reset. Use /profile to setup again.", call.message.chat.id, call.message.message_id)

# Search
@bot.message_handler(commands=['search'])
def random_search(message):
    if not check_force_join(message):
        return
    if message.from_user.id in chats:
        bot.send_message(message.chat.id, "❗️ You're already chatting. Use /disconnect first.")
        return
    searching.append(message.from_user.id)
    bot.send_message(message.chat.id, "🔍 Searching for partner...")
    match_users()

# Filter Search
@bot.message_handler(commands=['filtersearch'])
def filter_search(message):
    if not check_force_join(message):
        return
    if message.from_user.id in chats:
        bot.send_message(message.chat.id, "❗️ You're already chatting. Use /disconnect first.")
        return
    filter_searching.append(message.from_user.id)
    bot.send_message(message.chat.id, "🎯 Searching with filters...")
    match_users()

# Match
def match_users():
    random.shuffle(searching)
    while len(searching) >= 2:
        u1 = searching.pop(0)
        u2 = searching.pop(0)
        connect(u1, u2)

    random.shuffle(filter_searching)
    while len(filter_searching) >= 2:
        u1 = filter_searching.pop(0)
        u2 = filter_searching.pop(0)
        if check_filter(u1, u2):
            connect(u1, u2)

def check_filter(u1, u2):
    p1 = users.get(u1, {})
    p2 = users.get(u2, {})
    return (p1.get("gender") != p2.get("gender") and
            p1.get("country") == p2.get("country") and
            abs(int(p1.get("age", 0)) - int(p2.get("age", 0))) <= 5)

def connect(u1, u2):
    chats[u1] = u2
    chats[u2] = u1

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Disconnect", callback_data="disconnect"))

    bot.send_message(u1, f"❤️ Partner Found!\n\n{get_profile_text(u2)}", reply_markup=markup)
    bot.send_message(u2, f"❤️ Partner Found!\n\n{get_profile_text(u1)}", reply_markup=markup)

# Disconnect
@bot.callback_query_handler(func=lambda call: call.data == "disconnect")
def disconnect_call(call):
    disconnect_user(call.from_user.id)

@bot.message_handler(commands=['disconnect'])
def disconnect_cmd(message):
    disconnect_user(message.from_user.id)

def disconnect_user(uid):
    partner = chats.pop(uid, None)
    if partner:
        chats.pop(partner, None)
        bot.send_message(uid, "❌ Disconnected!")
        bot.send_message(partner, "❌ Disconnected!")
    else:
        bot.send_message(uid, "❗️ You are not chatting!")

# Fix Command
@bot.message_handler(commands=['fix'])
def fix(message):
    if message.from_user.id != ADMIN_ID:
        return
    ids = message.text.split()
    if len(ids) == 3:
        u1 = int(ids[1])
        u2 = int(ids[2])
        connect(u1, u2)
        bot.send_message(ADMIN_ID, "✅ Fixed Connection Done.")

# Block/Unblock
@bot.message_handler(commands=['block'])
def block(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) == 3:
        user_id = int(parts[1])
        until_time = parts[2]
        t = time.mktime(time.strptime(until_time, "%d%m%y"))
        blocked_users[user_id] = t
        bot.send_message(ADMIN_ID, f"🚫 User {user_id} blocked till {until_time}")

@bot.message_handler(commands=['unblock'])
def unblock(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) == 2:
        user_id = int(parts[1])
        blocked_users.pop(user_id, None)
        bot.send_message(ADMIN_ID, f"✅ User {user_id} unblocked!")

# Exchange
@bot.message_handler(commands=['exchange'])
def exchange(message):
    user = users.get(message.from_user.id, {})
    if referrals.get(message.from_user.id, 0) >= 3:
        user["points"] = user.get("points", 0) + 2
        referrals[message.from_user.id] -= 3
        bot.send_message(message.chat.id, "🎉 Exchanged 3 referrals for 2 hour filter access!")
    else:
        bot.send_message(message.chat.id, "❗️ You need 3 referrals to exchange!")

# Stop Search
@bot.message_handler(commands=['stopsearch'])
def stopsearch(message):
    if message.from_user.id in searching:
        searching.remove(message.from_user.id)
    if message.from_user.id in filter_searching:
        filter_searching.remove(message.from_user.id)
    bot.send_message(message.chat.id, "🛑 Search Stopped.")

# Run bot
print("Bot is running...")
bot.infinity_polling()
