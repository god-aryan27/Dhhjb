import telebot
from telebot import types
import time
import threading

# Your Bot Details
BOT_TOKEN = '8011013049:AAGVlTalTLZ-LI24aPflJM6Iptmb13W3Hvo'
bot = telebot.TeleBot(BOT_TOKEN)
CHANNEL_ID = -1002316557460
ADMIN_ID = 7401896933

# Data Storage
users = {}
waiting_random = []
waiting_filter = []
blocked_users = {}

# Helper functions
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Random Chat", "🎯 Filter Chat")
    markup.row("👤 Profile", "⚙️ Settings", "💰 Referral")
    return markup

def profile_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚻 Set Gender", callback_data="set_gender"))
    markup.add(types.InlineKeyboardButton("🎂 Set Age", callback_data="set_age"))
    markup.add(types.InlineKeyboardButton("🌎 Set Country", callback_data="set_country"))
    return markup

def setting_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Reset Settings", callback_data="reset_settings"))
    return markup

def genders_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♂️ Male", callback_data="gender_male"),
               types.InlineKeyboardButton("♀️ Female", callback_data="gender_female"))
    return markup

def countries_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🇮🇳 India", callback_data="country_india"),
        types.InlineKeyboardButton("🇮🇩 Indonesia", callback_data="country_indonesia")
    )
    markup.add(
        types.InlineKeyboardButton("🇰🇷 Korea", callback_data="country_korea"),
        types.InlineKeyboardButton("🇷🇺 Russia", callback_data="country_russia")
    )
    markup.add(
        types.InlineKeyboardButton("🇱🇰 Sri Lanka", callback_data="country_srilanka"),
        types.InlineKeyboardButton("🇺🇸 USA", callback_data="country_usa")
    )
    return markup

def age_markup():
    markup = types.InlineKeyboardMarkup()
    for age in range(18, 26):
        markup.add(types.InlineKeyboardButton(f"{age}", callback_data=f"age_{age}"))
    return markup

# Bot Commands
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if not is_member(user_id):
        join_markup = types.InlineKeyboardMarkup()
        join_markup.add(types.InlineKeyboardButton("✅ Join Channel", url="https://t.me/+g-i8Vohdrv44NDRl"))
        bot.send_message(user_id, "⚡ Please join our channel first!", reply_markup=join_markup)
        return

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
            "session": time.time() + 3600  # 1 Hour for new user
        }
        bot.send_message(ADMIN_ID, f"🎉 New User: [{user_id}](tg://user?id={user_id})", parse_mode="Markdown")

        if len(args) > 1:
            ref_code = args[1]
            try:
                ref_id = int(ref_code)
                if ref_id != user_id and ref_id in users:
                    users[ref_id]["referrals"] += 1
                    bot.send_message(ref_id, "🎯 You got 1 referral! 3 referrals = 2hr filter chat!")
                    bot.send_message(ADMIN_ID, f"📣 [{user_id}](tg://user?id={user_id}) used referral of [{ref_id}](tg://user?id={ref_id})", parse_mode="Markdown")
            except:
                pass

    bot.send_message(user_id, "👋 Welcome to Datingxrobot!", reply_markup=start_menu())

@bot.message_handler(commands=['fix'])
def fix_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        if len(parts) == 3:
            uid1 = int(parts[1])
            uid2 = int(parts[2])
            users[uid1]["partner"] = uid2
            users[uid2]["partner"] = uid1

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("❌ Disconnect", callback_data="disconnect"))

            bot.send_message(uid1, f"❤️ Admin connected you with [{uid2}](tg://user?id={uid2})!", parse_mode="Markdown", reply_markup=markup)
            bot.send_message(uid2, f"❤️ Admin connected you with [{uid1}](tg://user?id={uid1})!", parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error: {e}")

@bot.message_handler(commands=['disconnect'])
def disconnect_command(message):
    user_id = message.from_user.id
    partner = users.get(user_id, {}).get("partner")
    if partner:
        users[user_id]["partner"] = None
        users[partner]["partner"] = None
        bot.send_message(user_id, "❌ Disconnected.")
        bot.send_message(partner, "❌ Disconnected.")
    bot.send_message(user_id, "🏠 Back to Menu", reply_markup=start_menu())

@bot.message_handler(func=lambda m: True)
def main(message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in users:
        return start(message)

    if not is_member(user_id):
        join_markup = types.InlineKeyboardMarkup()
        join_markup.add(types.InlineKeyboardButton("✅ Join Channel", url="https://t.me/+g-i8Vohdrv44NDRl"))
        bot.send_message(user_id, "⚡ Please join our channel first!", reply_markup=join_markup)
        return

    if text == "🔍 Random Chat":
        if user_id in waiting_random:
            bot.send_message(user_id, "⏳ Already waiting...")
            return
        waiting_random.append(user_id)
        bot.send_message(user_id, "🔎 Searching for partner...")
        find_random_partner(user_id)

    elif text == "🎯 Filter Chat":
        if users[user_id]["session"] < time.time():
            bot.send_message(user_id, "⏳ You need more referrals to access filter chat!")
            return
        if user_id in waiting_filter:
            bot.send_message(user_id, "⏳ Already waiting...")
            return
        waiting_filter.append(user_id)
        bot.send_message(user_id, "🔎 Searching for matching partner...")
        find_filter_partner(user_id)

    elif text == "👤 Profile":
        bot.send_message(user_id, "👤 Update your profile:", reply_markup=profile_menu())

    elif text == "⚙️ Settings":
        bot.send_message(user_id, "⚙️ Settings:", reply_markup=setting_menu())

    elif text == "💰 Referral":
        bot.send_message(user_id, f"💬 Your Referral Link:\nhttps://t.me/Datingxrobot?start={user_id}")

def find_random_partner(user_id):
    for uid in waiting_random:
        if uid != user_id:
            waiting_random.remove(uid)
            waiting_random.remove(user_id)
            users[user_id]["partner"] = uid
            users[uid]["partner"] = user_id

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("❌ Disconnect", callback_data="disconnect"))

            info_user = f"❤️ Matched!\n\n🚻 Gender: {users[uid]['gender']}\n🎂 Age: {users[uid]['age']}\n🌎 Country: {users[uid]['country']}"
            info_partner = f"❤️ Matched!\n\n🚻 Gender: {users[user_id]['gender']}\n🎂 Age: {users[user_id]['age']}\n🌎 Country: {users[user_id]['country']}"

            bot.send_message(user_id, info_user, reply_markup=markup)
            bot.send_message(uid, info_partner, reply_markup=markup)
            return
    bot.send_message(user_id, "⏳ Waiting for partner...")

def find_filter_partner(user_id):
    for uid in waiting_filter:
        if uid != user_id:
            waiting_filter.remove(uid)
            waiting_filter.remove(user_id)
            users[user_id]["partner"] = uid
            users[uid]["partner"] = user_id

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("❌ Disconnect", callback_data="disconnect"))

            info_user = f"❤️ Matched!\n\n🚻 Gender: {users[uid]['gender']}\n🎂 Age: {users[uid]['age']}\n🌎 Country: {users[uid]['country']}"
            info_partner = f"❤️ Matched!\n\n🚻 Gender: {users[user_id]['gender']}\n🎂 Age: {users[user_id]['age']}\n🌎 Country: {users[user_id]['country']}"

            bot.send_message(user_id, info_user, reply_markup=markup)
            bot.send_message(uid, info_partner, reply_markup=markup)
            return
    bot.send_message(user_id, "⏳ Waiting for match...")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "disconnect":
        partner = users.get(user_id, {}).get("partner")
        if partner:
            users[user_id]["partner"] = None
            users[partner]["partner"] = None
            bot.send_message(user_id, "❌ Disconnected.")
            bot.send_message(partner, "❌ Disconnected.")
        bot.send_message(user_id, "🏠 Back to Menu", reply_markup=start_menu())

    elif call.data == "set_gender":
        bot.send_message(user_id, "🚻 Choose your gender:", reply_markup=genders_markup())

    elif call.data == "set_country":
        bot.send_message(user_id, "🌎 Choose your country:", reply_markup=countries_markup())

    elif call.data == "set_age":
        bot.send_message(user_id, "🎂 Choose your age:", reply_markup=age_markup())

    elif call.data == "reset_settings":
        users[user_id]["filter_gender"] = None
        users[user_id]["filter_age"] = None
        users[user_id]["filter_country"] = None
        bot.send_message(user_id, "✅ Filter settings reset!")

    elif call.data.startswith("gender_"):
        gender = call.data.split("_")[1]
        users[user_id]["gender"] = gender.capitalize()
        bot.send_message(user_id, f"✅ Gender set to {gender.capitalize()}!")

    elif call.data.startswith("country_"):
        country = call.data.split("_")[1]
        users[user_id]["country"] = country.capitalize()
        bot.send_message(user_id, f"✅ Country set to {country.capitalize()}!")

    elif call.data.startswith("age_"):
        age = call.data.split("_")[1]
        users[user_id]["age"] = age
        bot.send_message(user_id, f"✅ Age set to {age}!")

# Run Bot
print("Bot Running...")
bot.infinity_polling()
