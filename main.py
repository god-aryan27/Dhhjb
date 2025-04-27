# Let's create a sample professional-level bot code and compress it into a zip file.





# Sample Python script content

bot_code = 

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

import time



# --- SETTINGS ---

TOKEN = '8011013049:AAFStiHobHvvndOPMsEUyvOrN-Xlww24zms'  # Your Bot Token

FORCE_JOIN_CHANNEL = 'g-i8Vohdrv44NDRl'  # Channel username for force join

OPTIONAL_JOIN_LINK = 'https://t.me/+hrIjYhMdgMthNDI1'  # Optional channel link

FORCE_JOIN_CHANNEL_ID = -1002316557460  # Private channel ID for force join

ADMIN_ID = 7401896933  # Your Telegram ID (Admin)

SESSION_TIME = 3600  # 1 Hour

REFERRALS_REQUIRED = 3

EXTRA_TIME = 7200  # 2 Hours extra

# -----------------



users = {}

waiting_filter = []

waiting_random = []

partners = {}

referrals = {}



def start(update: Update, context: CallbackContext):

    user = update.effective_user

    chat_id = update.effective_chat.id

    

    if FORCE_JOIN_CHANNEL:

        member = context.bot.get_chat_member(FORCE_JOIN_CHANNEL, user.id)

        if member.status in ['left', 'kicked']:

            join_button = InlineKeyboardButton("Join Channel 📲", url=f"https://t.me/{FORCE_JOIN_CHANNEL[1:]}")

            markup = InlineKeyboardMarkup([[join_button]])

            update.message.reply_text("Please join our channel first to use the bot! 🙏", reply_markup=markup)

            return



    if user.id not in users:

        users[user.id] = {

            'gender': None,

            'age': None,

            'country': None,

            'session': time.time() + SESSION_TIME,

            'referrals': 0

        }

    

    join_button = InlineKeyboardButton("Join Extra Channel (Optional) 📢", url=OPTIONAL_JOIN_LINK)

    markup = InlineKeyboardMarkup([[join_button]])

    update.message.reply_text(

        "Welcome! You got 1 hour to use Filter Chat ⏳.\n\nPlease setup your profile first! 👤",

        reply_markup=markup

    )

    main_menu(update, context)



def main_menu(update: Update, context: CallbackContext):

    keyboard = [

        [KeyboardButton("Set Profile 📝"), KeyboardButton("My Profile 👤")],

        [KeyboardButton("Filter Chat 🔍"), KeyboardButton("Random Chat 🤖")],

        [KeyboardButton("End Chat ❌"), KeyboardButton("Refer Bot 📢")]

    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text("Choose an option:", reply_markup=markup)



def handle_text(update: Update, context: CallbackContext):

    text = update.message.text

    user_id = update.effective_user.id



    if text == "Set Profile 📝":

        gender_buttons = [

            [InlineKeyboardButton("Male 👦", callback_data="gender_male"),

             InlineKeyboardButton("Female 👧", callback_data="gender_female")]

        ]

        context.bot.send_message(user_id, "Select your gender 🏳️‍🌈:", reply_markup=InlineKeyboardMarkup(gender_buttons))

    

    elif text == "My Profile 👤":

        profile = users.get(user_id)

        if profile and profile['gender']:

            update.message.reply_text(

                f"Your Profile:\nGender: {profile['gender']} 👤\nAge: {profile['age']} 📅\nCountry: {profile['country']} 🌍"

            )

        else:

            update.message.reply_text("You haven't set your profile yet! 📝")



    elif text == "Filter Chat 🔍":

        profile = users.get(user_id)

        if profile and profile['gender']:

            if profile['session'] < time.time():

                update.message.reply_text("Your Filter Chat time expired! 😔 Refer friends to get more time ⏳.")

                return

            waiting_filter.append(user_id)

            update.message.reply_text("Waiting for a match... ⏳")

            match_filter(context)

        else:

            update.message.reply_text("Please set your profile first using 'Set Profile 📝'.")



    elif text == "Random Chat 🤖":

        waiting_random.append(user_id)

        update.message.reply_text("Searching for random partner... 🔍")

        match_random(context)



    elif text == "End Chat ❌":

        end_chat(user_id, context)



    elif text == "Refer Bot 📢":

        refer_link = f"https://t.me/{context.bot.username}?start={user_id}"

        update.message.reply_text(f"Invite friends using this link: {refer_link}\n\n3 referrals = 2 extra hours! ⏳")



def callback_query(update: Update, context: CallbackContext):

    query = update.callback_query

    user_id = query.from_user.id

    data = query.data



    if data.startswith("gender_"):

        gender = data.split("_")[1].capitalize()

        users[user_id]['gender'] = gender

        age_buttons = [

            [InlineKeyboardButton(str(i), callback_data=f"age_{i}") for i in range(18, 31, 2)]

        ]

        query.message.reply_text("Select your age 📅:", reply_markup=InlineKeyboardMarkup(age_buttons))

    

    elif data.startswith("age_"):

        age = data.split("_")[1]

        users[user_id]['age'] = age

        country_buttons = [

            [InlineKeyboardButton("India 🇮🇳", callback_data="country_India")],

            [InlineKeyboardButton("Pakistan 🇵🇰", callback_data="country_Pakistan")],

            [InlineKeyboardButton("USA 🇺🇸", callback_data="country_USA")],

            [InlineKeyboardButton("Other 🌍", callback_data="country_Other")]

        ]

        query.message.reply_text("Select your country 🌍:", reply_markup=InlineKeyboardMarkup(country_buttons))

    

    elif data.startswith("country_"):

        country = data.split("_")[1]

        users[user_id]['country'] = country

        query.message.reply_text("Profile setup completed! ✅")

        main_menu(update, context)



def match_filter(context: CallbackContext):

    if len(waiting_filter) >= 2:

        user1 = waiting_filter.pop(0)

        for i, user2 in enumerate(waiting_filter):

            if match_criteria(users[user1], users[user2]):

                partners[user1] = user2

                partners[user2] = user1

                waiting_filter.pop(i)

                send_profile(context, user1, user2)

                send_profile(context, user2, user1)

                break



def match_criteria(user1, user2):

    return (user1['gender'] != user2['gender'])



def match_random(context: CallbackContext):

    if len(waiting_random) >= 2:

        user1 = waiting_random.pop(0)

        user2 = waiting_random.pop(0)

        partners[user1] = user2

        partners[user2] = user1

        context.bot.send_message(user1, "Partner found! Say hi! 👋")

        context.bot.send_message(user2, "Partner found! Say hi! 👋")



def send_profile(context: CallbackContext, user_id, partner_id):

    partner = users[partner_id]

    context.bot.send_message(user_id,

        f"Partner Found! 👫\n\nGender: {partner['gender']} 👤\nAge: {partner['age']} 📅\nCountry: {partner['country']} 🌍\n\nSay Hi! 👋")



def end_chat(user_id, context: CallbackContext):

    if user_id in partners:

        partner_id = partners.pop(user_id)

        if partner_id in partners:

            partners.pop(partner_id)

            context.bot.send_message(partner_id, "Your partner left the chat! ❌")

        context.bot.send_message(user_id, "Chat ended. ❌")

    else:

        context.bot.send_message(user_id, "You are not in chat. ❓")



def handle_message(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    if user_id in partners:

        partner_id = partners[user_id]

        context.bot.send_message(partner_id, update.message.text)



def handle_start_referral(update: Update, context: CallbackContext):

    args = context.args

    user_id = update.effective_user.id

    if args:

        referrer_id = int(args[0])

        if referrer_id != user_id:

            referrals.setdefault(referrer_id, set()).add(user_id)

            if len(referrals[referrer_id]) >= REFERRALS_REQUIRED:

                if referrer_id in users:

                    users[referrer_id]['session'] += EXTRA_TIME

                    context.bot.send_message(referrer_id, "You got +2 hours for referring 3 users! ⏳")



def main():

    updater = Updater(TOKEN)

    dp = updater.dispatcher



    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("start", handle_start_referral, pass_args=True))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    dp.add_handler(CallbackQueryHandler(callback_query))

    dp.add_handler(MessageHandler(Filters.text & Filters.chat_type.private, handle_message))



    updater.start_polling()

    updater.idle()



if __name__ == '__main__':

    main()

