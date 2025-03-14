import logging
import os
import re
import io
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image

# Configure logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === BOT CONFIGURATION ===
TOKEN = "7927403888:AAGoAV8OVvrLDyzbICPPQRbq_NrDkDpeLog"
GIFT_CODE = "9556CDB67D00BD65FA6A25B6DA381139"  # Gift code to award
APP_NAME = "91 Play Club"  # Text that must appear in the screenshot

# File to store redeemed user IDs
REDEEMED_USERS_FILE = "redeemed_users.txt"

# Channel and registration links
WHATSAPP_LINK = "https://whatsapp.com/channel/0029VaDnDaD5q08TpUkZ1B1e"
TELEGRAM_LINK = "https://telegram.me/Official_91_Club_Game"
REGISTER_LINK = "https://91appb.com/#/register?invitationCode=737751699314"

# Animated GIF URL for visual flair (you can change it if desired)
ANIMATION_URL = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmp1bGkwanV1eWJqcTdwcGtzaXR4c2J0cmtpeWtpM3FqY2wyYTZlcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3vRebb6HyeIgvmQ8/giphy.gif"

# === MESSAGES ===
WELCOME_MESSAGE = (
    "🌟 <b>Welcome, Champion!</b> 🌟\n\n"
    "You're Using The <b>91 Club Reward Bot</b>.\n"
    "Send us a Clear Screenshot of Your App Rating That Shows The App Name <b>91 Play Club</b>.\n"
    "Remember: Each User Can Claim Only One Gift code.\n\n"
    "Let's Get Started! 🚀"
)

FAIL_MESSAGE = (
    "❌ <b>Oops!</b> We Could Not Verify Your Screenshot.\n\n"
    "Please Make Sure Your Screenshot Clearly Displays the App Name <b>91 Play Club</b>.\n"
    "If You Believe This is a Mistake, try Again."
)

ALREADY_REDEEMED_MESSAGE = (
    "⚠️ <b>Attention!</b>\n\n"
    "It Appears You've Already Claimed Your Gift Code. Each User May Only Receive One Gift Code.\n\n"
    "Here Are Our Channels and Registration link for More Updates:\n"
    "• <a href='{whatsapp}'>WhatsApp Channel</a>\n"
    "• <a href='{telegram}'>Telegram Channel</a>\n"
    "• <a href='{register}'>Register for Extra Bonus</a>"
).format(whatsapp=WHATSAPP_LINK, telegram=TELEGRAM_LINK, register=REGISTER_LINK)

REWARD_MESSAGE = (
    f"🎉 <b>Congratulations!</b> 🎉\n\n"
    f"<b>Here is Your Exclusive Gift Code Of 91 Club</b> :- <code>{GIFT_CODE}</code>\n\n"
    "💎 <b>Join our Channels For high-accuracy predictions and free gift codes:</b>\n"
    "• Stay updated with exclusive tips and rewards!\n\n"
    "<b>Register on 91 Club</b> with the link below to receive an extra bonus."
)


# === PERSISTENCE FUNCTIONS ===
def load_redeemed_users(filename=REDEEMED_USERS_FILE):
    """Load redeemed user IDs from a file into a set."""
    if not os.path.exists(filename):
        return set()
    with open(filename, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

def save_redeemed_user(user_id, filename=REDEEMED_USERS_FILE):
    """Append a new user ID to the redeemed users file."""
    with open(filename, "a") as f:
        f.write(f"{user_id}\n")

# === INLINE KEYBOARD BUILDER ===
def build_reward_reply_markup():
    """
    Build an inline keyboard with beautifully styled buttons for WhatsApp, Telegram, and Registration.
    Note: While Telegram inline keyboards can't animate, the use of emojis and formatting helps create an engaging design.
    """
    keyboard = [
        [InlineKeyboardButton("💬 WhatsApp Channel", url=WHATSAPP_LINK)],
        [InlineKeyboardButton("🚀 Telegram Channel", url=TELEGRAM_LINK)],
        [InlineKeyboardButton("🎁 Register & Get Bonus", url=REGISTER_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a stylish welcome message when the user types /start."""
    await update.message.reply_html(WELCOME_MESSAGE, reply_markup=ForceReply(selective=True))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Process an incoming photo:
      1. Check if the user has already redeemed a gift code.
      2. Run OCR on the photo to verify it contains the app name "91 Play Club".
      3. If verified, mark the user as redeemed and send an animated GIF with the reward message and inline buttons.
      4. If not, send a failure message.
    """
    user = update.effective_user
    redeemed_users = load_redeemed_users()

    if user.id in redeemed_users:
        await update.message.reply_html(ALREADY_REDEEMED_MESSAGE)
        return

    # Download the photo and extract text using OCR
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))
    ocr_text = pytesseract.image_to_string(image)
    logger.info("OCR extracted text:\n%s", ocr_text)

    # Verify that the screenshot includes the app name "91 Play Club"
    if re.search(r"91\s*play\s*club", ocr_text, re.IGNORECASE) is None:
        await update.message.reply_html(FAIL_MESSAGE)
        return

    # Mark the user as redeemed
    save_redeemed_user(user.id)

    # Send an animated GIF with the reward message and inline buttons
    await update.message.reply_animation(
        animation=ANIMATION_URL,
        caption=REWARD_MESSAGE,
        parse_mode="HTML",
        reply_markup=build_reward_reply_markup()
    )

# === MAIN FUNCTION ===
def main() -> None:
    """Initialize the bot and start polling for updates."""
    application = Application.builder().token(TOKEN).build()

    # Register command and photo handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
