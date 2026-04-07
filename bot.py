import telebot
import requests
import json
import time
import os
from telebot import types
from flask import Flask
from threading import Thread
from datetime import datetime

# ================= KEEP ALIVE SERVER =================
app = Flask('')
@app.route('/')
def home(): return "Vikash Master bot is Online!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# =====================================================

# --- CONFIG (Apni Details Check Karein) ---
API_TOKEN = '8798135590:AAHBagHddN9kQnalWJ306LfisH9O22MRz5c' 
FIREBASE_URL = "https://telegrambot-22bce-default-rtdb.firebaseio.com"
DEVELOPER_ID = 7683645861
ADMIN_IDS = [7683645861, 8467097069] 
CHANNEL_LINK = "https://t.me/vikashsahu09" 
BOT_USERNAME = "vsinformation_bot"

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE HELPERS ---
def get_user_data(user_id):
    url = f"{FIREBASE_URL}/users/{user_id}.json"
    try:
        res = requests.get(url, timeout=10).json()
        if not res:
            res = {'credits': 20, 'is_blocked': False, 'is_premium': False, 'last_bonus': "2000-01-01"}
            requests.put(url, json.dumps(res))
        return res
    except: return {'credits': 0, 'is_blocked': True}

def update_user_data(user_id, update_dict):
    requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json.dumps(update_dict))

def get_all_users():
    try:
        res = requests.get(f"{FIREBASE_URL}/users.json").json()
        return res if res else {}
    except: return {}

# ================= KEYBOARD MENU =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [
        "🚗 Vehicle Scan", "📞 Number Search", 
        "🎮 Free Fire Info", "📱 IMEI Check", 
        "🏦 IFSC Finder", "🌐 IP Tracker", 
        "🎁 Daily Bonus", "🤝 Refer & Earn", 
        "👤 My Profile"
    ]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

# ================= ADMIN PANEL =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS: return
    text = (
        "🛠 **ROOT ADMIN PANEL** 🛠\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📢 `/broadcast [msg]` - Global Msg\n"
        "💰 `/addall [amt]` - Add to ALL\n"
        "🔄 `/resetall` - Set ALL to 0 Credits\n"
        "👑 `/setpre [id]` - Give Premium\n"
        "❌ `/rempre [id]` - Remove Premium\n"
        "💳 `/add [id] [amt]` | `/rem [id] [amt]`\n"
        "🚫 `/ban [id]` | ✅ `/unban [id]`\n"
        "📊 `/stats` - Total Users"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast', 'addall', 'resetall', 'add', 'rem', 'ban', 'unban', 'setpre', 'rempre', 'stats'])
def admin_actions(message):
    if message.from_user.id not in ADMIN_IDS: return
    cmd = message.text.split(maxsplit=2)
    action = cmd[0].replace('/', '')

    try:
        if action == 'broadcast':
            msg_text = cmd[1]
            users = get_all_users()
            count = 0
            wait_msg = bot.reply_to(message, "📡 **Broadcasting...**")
            for user_id in users:
                try:
                    bot.send_message(user_id, f"⚠️ **SYSTEM ALERT**\n\n{msg_text}", parse_mode="Markdown")
                    count += 1
                except: pass
            bot.edit_message_text(f"✅ Broadcast Sent to `{count}` users.", message.chat.id, wait_msg.message_id)

        elif action == 'addall':
            amt = int(cmd[1])
            users = get_all_users()
            count = 0
            wait_msg = bot.reply_to(message, f"💰 Adding {amt} Credits to everyone...")
            for user_id in users:
                try:
                    u_data = get_user_data(user_id)
                    update_user_data(user_id, {'credits': u_data['credits'] + amt})
                    count += 1
                except: pass
            bot.edit_message_text(f"✅ Success! Added to `{count}` users.", message.chat.id, wait_msg.message_id)

        elif action == 'resetall':
            users = get_all_users()
            count = 0
            wait_msg = bot.reply_to(message, "🔄 **Resetting all credits...**")
            for user_id in users:
                try:
                    update_user_data(user_id, {'credits': 0})
                    count += 1
                except: pass
            bot.edit_message_text(f"✅ Reset Complete for `{count}` users.", message.chat.id, wait_msg.message_id)

        elif action == 'setpre':
            target_id = cmd[1]
            update_user_data(target_id, {'is_premium': True, 'credits': 99999})
            bot.reply_to(message, f"👑 User `{target_id}` is now a Premium member!")

        elif action == 'rempre':
            target_id = cmd[1]
            update_user_data(target_id, {'is_premium': False, 'credits': 20})
            bot.reply_to(message, f"❌ Premium access removed for `{target_id}`. Credits reset to 20.")

        elif action == 'stats':
            users = get_all_users()
            bot.reply_to(message, f"📊 **Total Users:** `{len(users)}`")

        elif action == 'add':
            u_id, amt = cmd[1], int(cmd[2])
            u = get_user_data(u_id)
            update_user_data(u_id, {'credits': u['credits'] + amt})
            bot.reply_to(message, f"✅ Added `{amt}` Credits to `{u_id}`")

        elif action == 'rem':
            u_id, amt = cmd[1], int(cmd[2])
            u = get_user_data(u_id)
            new_credits = max(0, u['credits'] - amt)
            update_user_data(u_id, {'credits': new_credits})
            bot.reply_to(message, f"📉 Removed Credits from `{u_id}`.")

        elif action == 'ban':
            update_user_data(cmd[1], {'is_blocked': True})
            bot.reply_to(message, f"🚫 User `{cmd[1]}` Banned.")

        elif action == 'unban':
            update_user_data(cmd[1], {'is_blocked': False})
            bot.reply_to(message, f"✅ User `{cmd[1]}` Unbanned.")

    except Exception as e: bot.reply_to(message, f"❌ **Admin Error:** `{e}`")

# ================= MAIN OS INTERFACE =================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    access_type = "ROOT ADMIN" if user_id in ADMIN_IDS else "GUEST ACCESS"
    
    os_design = (
        "╔══════════════════════════════╗\n"
        "      ⚡ VIKASH MASTER OS ⚡\n"
        "╚══════════════════════════════╝\n\n"
        f"👤 USER: {user_name}\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔐 ACCESS: {access_type}\n"
        "🟢 STATUS: CONNECTED\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 AI ENGINE: ONLINE\n"
        "🛡️ FIREWALL: ACTIVE\n"
        "📡 SIGNAL: STRONG\n"
        "⚙️ SYSTEM LOAD: NORMAL\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ ALERT: No Threats Detected\n\n"
        f"💬 Welcome back, {user_name}...\n"
        "System is under your full control.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        ">>> READY FOR COMMAND ✅\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 SELECT OPERATION:"
    )
    bot.send_message(message.chat.id, os_design, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_all_text(message):
    user_id = message.from_user.id
    u = get_user_data(user_id)
    if u.get('is_blocked'): 
        return bot.send_message(message.chat.id, "🚫 **Access Denied!** System Blocked.")

    if message.text == "👤 My Profile":
        plan = "👑 Premium" if u.get('is_premium') else "🆓 Free"
        profile = (
            "👤 **USER PROFILE**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"💰 Credits: {u.get('credits', 0)}\n"
            f"⭐ Plan: {plan}\n\n"
            f"👨‍💻 Dev: [Vikash Sahu](tg://user?id={DEVELOPER_ID})\n"
            f"📢 [Join Channel]({CHANNEL_LINK})"
        )
        return bot.send_message(message.chat.id, profile, parse_mode="Markdown", disable_web_page_preview=True)

    if message.text == "🤝 Refer & Earn":
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        return bot.reply_to(message, f"🤝 **REFERRAL SYSTEM**\nInvite friends & get **5 Credits**!\n\n🔗 Link: `{link}`", parse_mode="Markdown")

    if message.text == "🎁 Daily Bonus":
        today = datetime.now().strftime("%Y-%m-%d")
        if u.get('last_bonus') == today: return bot.reply_to(message, "❌ **Denied!** Claimed already today.")
        update_user_data(user_id, {'credits': u['credits'] + 15, 'last_bonus': today})
        return bot.reply_to(message, "🎁 **Injected!** 15 Credits added.")

    service_map = {
        "🚗 Vehicle Scan": "rc", "📞 Number Search": "num", 
        "🎮 Free Fire Info": "ff", "📱 IMEI Check": "imei", 
        "🏦 IFSC Finder": "ifsc", "🌐 IP Tracker": "ip"
    }

    if message.text in service_map:
        service = service_map[message.text]
        msg = bot.send_message(message.chat.id, f"📡 **Enter {message.text} Target:**")
        bot.register_next_step_handler(msg, process_search, service)

def process_search(message, service):
    user_id = message.from_user.id
    u = get_user_data(user_id)
    target = message.text.strip().upper()
    if u['credits'] < 5 and not u['is_premium']: return bot.reply_to(message, "⚠️ **Credits Low!** 5 needed.")

    wait = bot.reply_to(message, "⚙️ **Scanning Database...**")
    api_urls = {
        "rc": f"https://vehicle-api-info-suruzxxr.vercel.app/vehicle-info?rc={target}",
        "num": f"http://exploitsindia.site/anish/api.php?key=anish&num={target}",
        "imei": f"https://ng-imei-info.vercel.app/?imei_num={target}",
        "ff": f"https://anku-ffapi-inky.vercel.app/ff?uid={target}",
        "ifsc": f"https://ifsc.razorpay.com/{target}",
        "ip": f"http://ip-api.com/json/{target}"
    }

    try:
        response = requests.get(api_urls[service], timeout=20)
        res = response.json()
        formatted = f"✨ **{service.upper()} SCAN RESULT** ✨\n━━━━━━━━━━━━━━\n"
        if isinstance(res, dict):
            for k, v in list(res.items())[:12]:
                if isinstance(v, (str, int, bool)):
                    formatted += f"🔹 {k.title().replace('_',' ')}: `{v}`\n"
        formatted += f"\n📊 **TECHNICAL DATA:**\n```json\n{json.dumps(res, indent=2)}\n```"
        bot.edit_message_text(formatted[:4096], message.chat.id, wait.message_id, parse_mode="Markdown")
        if not u['is_premium']: update_user_data(user_id, {'credits': u['credits'] - 5})
    except:
        bot.edit_message_text("❌ **FAILED!** Error connecting to API.", message.chat.id, wait.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
