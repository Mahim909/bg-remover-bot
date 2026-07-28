import asyncio
import io
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from rembg import remove

# 🔑 ১. আপনার টেলিগ্রাম বোট টোকেন
BOT_TOKEN = "8648016296:AAGr1t2DXQiSKWxLh2BEOHCEZodeuZYoTxo"

# 📢 ২. আপনার Monetag Direct Link
MONETAG_AD_LINK = "https://omg10.com/4/10346272"

# ⏱️ অপেক্ষা করার সময় (সেকেন্ডে)
WAIT_SECONDS = 6

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ইউজারদের ব্যাকগ্রাউন্ড রিমুভ করা ইমেজ ডাটা ক্যাশে রাখার জন্য ডিকশনারি
user_images = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋 Please send me any photo to remove its background."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    status_msg = await update.message.reply_text(
        "⏳ Processing your image... Please wait a moment."
    )

    try:
        # ১. ফাইল ডাউনলোড
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # ২. rembg দিয়ে ব্যাকগ্রাউন্ড রিমুভ
        output_bytes = remove(photo_bytes)

        # ৩. প্রসেসড ইমেজ ডাটা ইউজারের আইডি অনুযায়ী সাময়িকভাবে মেমোরিতে সেভ রাখা
        user_images[user_id] = output_bytes

        # ৪. ২-ধাপের বাটন সেটআপ (Ads + Get Image)
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎁 1. Tap Ads Link", url=MONETAG_AD_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    "📥 2. Get Image", callback_data="get_image"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # ৫. ইউজারকে ইন্সট্রাকশন দেওয়া
        await update.message.reply_text(
            "✅ *Your Image is Ready!*\n\n"
            "👉 **Step 1:** Tap the **Ads Link** below.\n"
            "👉 **Step 2:** Tap **Get Image** button and wait 6 seconds to receive your photo.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(
            "❌ Failed to process the image. Please try sending a clearer photo!"
        )
        print(f"Error: {e}")


# "Get Image" বাটনে ক্লিক করলে এই ফাংশন কাজ করবে
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "get_image":
        if user_id in user_images:
            # ৬ সেকেন্ডের কাউন্টডাউন / ওয়েটিং মেসেজ
            msg = await query.message.reply_text(
                "⏳ Checking ad view... Please wait **6 seconds**.",
                parse_mode="Markdown",
            )

            # ⏱️ ঠিক ৬ সেকেন্ড অপেক্ষা করবে
            await asyncio.sleep(WAIT_SECONDS)

            # ৬ সেকেন্ড পর ফাইনাল ফটো পাঠাবে
            output_bytes = user_images[user_id]
            await query.message.reply_document(
                document=io.BytesIO(output_bytes),
                filename="no_bg.png",
                caption="🎉 Thank you for waiting! Here is your background-removed image.",
            )

            # ক্যাশ থেকে ডাটা মুছে ফেলা
            del user_images[user_id]
            await msg.delete()
        else:
            await query.message.reply_text(
                "❌ Session expired or image not found. Please send the photo again!"
            )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot is running with 6s Ad delay...")
    app.run_polling()


if __name__ == "__main__":
    main()
