import os
import requests
import qrcode
import stepic
import logging
from PIL import Image
from io import BytesIO
from gtts import gTTS
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Bot Token (BotFather se lein) ---
TOKEN = '8725822200:AAHWzwTk2jEOnwRdd4Ey10ba_kIaSH8I0js'

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Keyboard Setup ---
# Isse user ko sirf button dabana hoga
main_menu = [
    [KeyboardButton("👤 GitHub Info"), KeyboardButton("📍 IP Tracker")],
    [KeyboardButton("📱 QR Generator"), KeyboardButton("🗣 Text to Voice")],
    [KeyboardButton("📮 Pincode Info"), KeyboardButton("🏦 IFSC Lookup")],
    [KeyboardButton("🖼 YT Thumbnail"), KeyboardButton("🔗 File to Link")],
    [KeyboardButton("🔐 Hide Message"), KeyboardButton("🔓 Extract Message")]
]
markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hi! Main Vikash ka Advance Multi-Tool Bot hoon.\n\nNiche diye gaye buttons ka use karein. Kisi bhi tool ki 'Usage' jaanne ke liye us button ko dabayein.",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Simple UI logic for buttons
    if text == "👤 GitHub Info":
        await update.message.reply_text("Usage: `/github username` likh kar bhejein.")
    elif text == "📍 IP Tracker":
        await update.message.reply_text("Usage: `/ip 8.8.8.8` likh kar bhejein.")
    elif text == "📱 QR Generator":
        await update.message.reply_text("Usage: `/qr your_text` likh kar bhejein.")
    elif text == "🗣 Text to Voice":
        await update.message.reply_text("Usage: `/tts Aapka Message` likh kar bhejein.")
    elif text == "📮 Pincode Info":
        await update.message.reply_text("Usage: `/pin 452001` likh kar bhejein.")
    elif text == "🏦 IFSC Lookup":
        await update.message.reply_text("Usage: `/ifsc SBIN0000001` likh kar bhejein.")
    elif text == "🖼 YT Thumbnail":
        await update.message.reply_text("Usage: `/thumb video_link` likh kar bhejein.")
    elif text == "🔗 File to Link":
        await update.message.reply_text("📁 Bas koi bhi File ya Document bot ko bhejein, link turant mil jayega.")
    elif text == "🔐 Hide Message":
        await update.message.reply_text("📸 Ek Photo bhejein aur uske 'Caption' me `/hide SecretMessage` likhein.")
    elif text == "🔓 Extract Message":
        await update.message.reply_text("🖼 Wo Photo (as Document) bhejein jisme message chhupa hai aur caption me `/extract` likhein.")

# --- Action Logic ---

async def github_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    res = requests.get(f"https://api.github.com/users/{context.args[0]}").json()
    msg = f"👤 Name: {res.get('name')}\n📂 Repos: {res.get('public_repos')}\n👥 Followers: {res.get('followers')}"
    await update.message.reply_text(msg)

async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    d = requests.get(f"http://ip-api.com/json/{context.args[0]}").json()
    msg = f"📍 City: {d.get('city')}\n🌍 Country: {d.get('country')}\n🌐 ISP: {d.get('isp')}"
    await update.message.reply_text(msg)

async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    img = qrcode.make(" ".join(context.args))
    img.save("q.png")
    await update.message.reply_photo(photo=open("q.png", 'rb'))
    os.remove("q.png")

async def tts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    tts = gTTS(" ".join(context.args), lang='hi')
    tts.save("v.mp3")
    await update.message.reply_audio(audio=open("v.mp3", 'rb'))
    os.remove("v.mp3")

async def pin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    res = requests.get(f"https://api.postalpincode.in/pincode/{context.args[0]}").json()
    if res[0]['Status'] == 'Success':
        p = res[0]['PostOffice'][0]
        await update.message.reply_text(f"📍 Area: {p['Name']}, {p['State']}")

async def ifsc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    res = requests.get(f"https://ifsc.razorpay.com/{context.args[0]}").json()
    await update.message.reply_text(f"🏦 Bank: {res.get('BANK')}\n📍 Branch: {res.get('BRANCH')}")

async def thumb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    url = context.args[0]
    vid_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
    await update.message.reply_photo(photo=f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg")

# --- Special Tools (File & Stego) ---

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check for Extract
    caption = update.message.caption or ""
    if "/extract" in caption.lower():
        doc = await update.message.document.get_file()
        img = Image.open(BytesIO(await doc.download_as_bytearray()))
        try:
            msg = stepic.decode(img)
            await update.message.reply_text(f"🔓 Hidden Message: `{msg}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Is photo me koi message nahi mila.")
    else:
        # File to link
        file = await update.message.document.get_file()
        f_bytes = await file.download_as_bytearray()
        res = requests.post('https://file.io', files={'file': f_bytes}).json()
        await update.message.reply_text(f"🔗 Link: {res['link']}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or ""
    if "/hide" in caption.lower():
        msg = caption.replace("/hide", "").strip()
        photo = await update.message.photo[-1].get_file()
        img = Image.open(BytesIO(await photo.download_as_bytearray()))
        secret_img = stepic.encode(img, msg.encode())
        out = BytesIO()
        secret_img.save(out, format="PNG")
        out.seek(0)
        await update.message.reply_document(document=out, filename="secret.png", caption="✅ Done!")

# --- Main ---

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("github", github_info if 'github_info' in globals() else github_cmd))
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("tts", tts_cmd))
    app.add_handler(CommandHandler("pin", pin_cmd))
    app.add_handler(CommandHandler("ifsc", ifsc_cmd))
    app.add_handler(CommandHandler("thumb", thumb_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🚀 Vikash Bot is Live!")
    app.run_polling()

if __name__ == '__main__':
    main()
