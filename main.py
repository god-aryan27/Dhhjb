import telebot
import os
from datetime import datetime

TOKEN = os.getenv('TOKEN') or '8011013049:AAGVlTalTLZ-LI24aPflJM6Iptmb13W3Hvo'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7401896933
CHANNEL_ID = -1002316557460  # Your private channel ID

users = {}
waiting_random = []
waiting_filter = []
blocked_users = {}

# Helper Functions
def is_blocked(user_id):
    unblock_date = blocked_users.get(user_id)
    if unblock_date and datetime.now() < unblock_date:
        return True
    return False

def check_force_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def user_profile_complete(user_id):
    user = users.get(user_id)
    return user and user.get('gender') and user.get('age') and user.get('country')

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Random Chat", "🎯 Filter Chat")
    markup.add("👤 Profile", "🎁 Referral")
    markup.add("💰 Exchange Points", "⚙️ Settings")
    return markup

def chatting_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ /disconnect")
    return markup

def stop_search_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Stop Searching")
    return markup

def profile_info(user_id):
    user = users.get(user_id, {})
    return f"👤 Gender: {user.get('gender')}\n🎂 Age: {user.get('age')}\n🌎 Country: {user.get('country')}"

# Country list with the 5 additional countries
COUNTRIES = [
    "🇮🇳 India", "🇺🇸 USA", "🇬🇧 UK", "🇨🇦 Canada", "🇦🇺 Australia",
    "🇮🇩 Indonesia", "🇰🇷 Korea", "🇷🇺 Russia", "🇱🇰 Sri Lanka", "🇯🇵 Japan"
]

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_blocked(user_id):
        bot.send_message(user_id, "⛔ You are blocked.")
        return

    if not check_force_join(user_id):
        bot.send_message(user_id, "🔒 Please join our channel first:\n👉 [Join Now](https://t.me/+g-i8Vohdrv44NDRl)", parse_mode="Markdown")
        return

    args = message.text.split()
    referred_by = None
    if len(args) > 1:
        referred_by = args[1]

    if user_id not in users:
        users[user_id] = {
            "gender": None,
            "age": None,
            "country": None,
            "referrals": 0,
            "referred_by": referred_by,
            "points": 0,
            "filter_hours": 1, 
            "connected_to": None
        }
        if referred_by and referred_by.isdigit() and int(referred_by) != user_id and int(referred_by) in users:
            users[int(referred_by)]['referrals'] += 1
            bot.send_message(int(referred_by), "🎉 You referred a new user! Total referrals: {}".format(users[int(referred_by)]['referrals']))
            bot.send_message(ADMIN_ID, f"👥 New Referral:\nUser {user_id} referred by {referred_by}")

    bot.send_message(user_id, "👋 Welcome to DatingxRobot!\nLet's setup your profile.\n\nWhat's your gender?", reply_markup=gender_markup())

# Gender Selection
def gender_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("👨 Male", "👩 Female")
    return markup

@bot.message_handler(func=lambda m: m.text in ["👨 Male", "👩 Female"])
def set_gender(message):
    user_id = message.from_user.id
    if not users.get(user_id):
        return

    users[user_id]['gender'] = "Male" if "Male" in message.text else "Female"
    bot.send_message(user_id, "📅 Select your age:", reply_markup=age_inline_markup())

def age_inline_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    for age in range(18, 101, 1):
        markup.add(telebot.types.InlineKeyboardButton(str(age), callback_data=f"set_age_{age}"))
    return markup

@bot.message_handler(func=lambda m: users.get(m.from_user.id) and users[m.from_user.id].get('gender') and not users[m.from_user.id].get('age'))
def set_country(message):
    user_id = message.from_user.id
    country = message.text.strip()
    users[user_id]['country'] = country
    bot.send_message(user_id, "✅ Profile set!\nUse the menu below:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_age_"))
def set_age(call):
    user_id = call.from_user.id
    age = int(call.data.split("_")[2])
    users[user_id]['age'] = age
    bot.send_message(user_id, "🌎 Enter your country:", reply_markup=country_inline_markup())

def country_inline_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    for country in COUNTRIES:
        markup.add(telebot.types.InlineKeyboardButton(country, callback_data=f"set_country_{country}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_country_"))
def set_country_inline(call):
    user_id = call.from_user.id
    country = call.data.split("_")[2]
    users[user_id]['country'] = country
    bot.send_message(user_id, "✅ Profile set!\nUse the menu below:", reply_markup=main_menu())

# Profile Button
@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):
    user_id = message.from_user.id
    if not user_profile_complete(user_id):
        bot.send_message(user_id, "⚙️ Please complete your profile first.")
        return
    bot.send_message(user_id, f"👤 Your Profile:\n\n{profile_info(user_id)}")

# Reset Settings
@bot.message_handler(func=lambda m: m.text == "⚙️ Settings")
def settings(message):
    user_id = message.from_user.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔄 Reset Settings", "🔙 Back to Menu")
    bot.send_message(user_id, "⚙️ Settings:\nChoose an option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔄 Reset Settings")
def reset_settings(message):
    user_id = message.from_user.id
    if not users.get(user_id):
        return
    users[user_id]['gender'] = None
    users[user_id]['age'] = None
    users[user_id]['country'] = None
    bot.send_message(user_id, "✅ Settings reset! Please set your profile again.", reply_markup=gender_markup())

# Random Chat
@bot.message_handler(func=lambda m: m.text == "🔍 Random Chat")
def random_chat(message):
    user_id = message.from_user.id
    if is_blocked(user_id):
        bot.send_message(user_id, "⛔ You are blocked.")
        return
    if users[user_id]['connected_to']:
        bot.send_message(user_id, "⚠️ Already connected! Use /disconnect.")
        return
    waiting_random.append(user_id)
    bot.send_message(user_id, "🔎 Searching for a random partner...", reply_markup=stop_search_markup())
    match_random_users()

def match_random_users():
    while len(waiting_random) >= 2:
        user1 = waiting_random.pop(0)
        user2 = waiting_random.pop(0)

        users[user1]['connected_to'] = user2
        users[user2]['connected_to'] = user1

        bot.send_message(user1, f"❤️ Connected!\n\n{profile_info(user2)}", reply_markup=chatting_markup())
        bot.send_message(user2, f"❤️ Connected!\n\n{profile_info(user1)}", reply_markup=chatting_markup())

# Stop Searching
@bot.message_handler(func=lambda m: m.text == "❌ Stop Searching")
def stop_search(message):
    user_id = message.from_user.id
    if user_id in waiting_random:
        waiting_random.remove(user_id)
        bot.send_message(user_id, "❌ Stopped searching.", reply_markup=main_menu())
    elif user_id in waiting_filter:
        waiting_filter.remove(user_id)
        bot.send_message(user_id, "❌ Stopped searching.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "⚠️ You are not searching.")

# Disconnect Command
@bot.message_handler(commands=['disconnect'])
def disconnect(message):
    user_id = message.from_user.id
    partner_id = users.get(user_id, {}).get('connected_to')

    if partner_id:
        users[user_id]['connected_to'] = None
        users[partner_id]['connected_to'] = None
        bot.send_message(user_id, "❌ Disconnected.", reply_markup=main_menu())
        bot.send_message(partner_id, "❌ Partner disconnected.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "⚠️ You are not connected.")

# Fix Command for Admin
@bot.message_handler(commands=['fix'])
def fix_connect(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) != 3:
        bot.send_message(user_id, "⚠️ Usage: /fix USER1 USER2")
        return

    user1 = int(args[1])
    user2 = int(args[2])

    users[user1]['connected_to'] = user2
    users[user2]['connected_to'] = user1

    bot.send_message(user1, f"❤️ Admin connected you manually with:\n\n{profile_info(user2)}", reply_markup=chatting_markup())
    bot.send_message(user2, f"❤️ Admin connected you manually with:\n\n{profile_info(user1)}", reply_markup=chatting_markup())

# Bot Runner
def run_bot():
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
