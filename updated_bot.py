# نسخه نهایی و کامل ربات محاسبه حقوق و آموزش بازرگانی
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

CHOOSING, SELECT_CURRENCY, ARZ, FOB, BIME, HAMl, MAKHAZ, PASMAND, EDU_MENU = range(9)
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🎉 خوش آمدید به ربات رسمی ترخیص آنلاین! 🇮🇷📦

با این ربات می‌توانید:
✅ محاسبات دقیق حقوق و عوارض گمرکی را انجام دهید
📚 با مفاهیم مهم بازرگانی آشنا شوید

👇 لطفاً از منوی زیر یکی را انتخاب کنید:
    """
    keyboard = [["محاسبه حقوق و عوارض گمرکی"], ["آموزش بازرگانی"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return CHOOSING


async def show_menu(update):
    keyboard = [["محاسبه حقوق و عوارض گمرکی"], ["آموزش بازرگانی"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("منوی اصلی:", reply_markup=reply_markup)
    return CHOOSING


async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "محاسبه" in text:
        currency_keyboard = [["دلار", "یورو"], ["یوان", "درهم"]]
        reply_markup = ReplyKeyboardMarkup(currency_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "لطفاً نوع ارز را انتخاب کنید:", reply_markup=reply_markup
        )
        return SELECT_CURRENCY
    elif "آموزش" in text:
        keyboard = [["اسناد حمل", "اینکوترمز"], ["ثبت سفارش", "ترخیص کالا"], ["بازگشت"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "یک موضوع آموزشی را انتخاب کنید:", reply_markup=reply_markup
        )
        return EDU_MENU
    else:
        await update.message.reply_text("❌ لطفاً یکی از گزینه‌های منو را انتخاب کنید.")
        return CHOOSING


async def select_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["currency"] = update.message.text.strip()
    await update.message.reply_text(
        f"لطفاً نرخ ارز ({user_data['currency']}) را وارد کنید:"
    )
    return ARZ


async def get_arz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["arz"] = int(update.message.text)
        await update.message.reply_text("ارزش فوب کالا را وارد کنید:")
        return FOB
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return ARZ


async def get_fob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["fob_dollar"] = float(update.message.text)
        await update.message.reply_text("مبلغ بیمه (ریال) را وارد کنید:")
        return BIME
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return FOB


async def get_bime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["bime"] = float(update.message.text)
        await update.message.reply_text("مبلغ کرایه حمل (ریال) را وارد کنید:")
        return HAMl
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return BIME


async def get_haml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["haml"] = int(update.message.text)
        await update.message.reply_text("درصد ماخذ را وارد کنید:")
        return MAKHAZ
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return HAMl


async def get_makhaz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["makhaz"] = float(update.message.text)
        await update.message.reply_text("آیا محاسبه پسماند انجام شود؟ (بله / خیر)")
        return PASMAND
    except:
        await update.message.reply_text("❌ فقط عدد وارد کنید:")
        return MAKHAZ


async def get_pasmand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pasmand_input = update.message.text.strip().lower()
    user_data["pasmand"] = pasmand_input in [
        "بله",
        "بلی",
        "آره",
        "آری",
        "yes",
        "y",
        "baale",
        "are",
    ]

    arz = user_data["arz"]
    fob_dollar = user_data["fob_dollar"]
    fob = arz * fob_dollar
    bime = user_data["bime"]
    haml = user_data["haml"]
    makhaz = user_data["makhaz"]

    cif = fob + bime + haml
    hoghogh = (cif * makhaz) / 100
    helal = (hoghogh * 1) / 100
    pasmand = (cif * 0.5) / 1000 if user_data["pasmand"] else 0
    vat = (cif + hoghogh + helal) * 0.10
    total = hoghogh + helal + vat

    result = f"""
📦 نتایج محاسبه:
➖➖➖
🔹 ارزش CIF: {round(cif):,} ریال
🔸 حقوق ورودی: {round(hoghogh):,} ریال
🩺 هلال احمر (۱٪): {round(helal):,} ریال
♻️ پسماند: {round(pasmand):,} ریال
💰 مالیات: {round(vat):,} ریال
💳 جمع کل پرداختی: {round(total):,} ریال
➖➖➖
    """
    await update.message.reply_text(result)
    return await show_menu(update)


async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "اسناد" in text:
        msg = """
📄 اسناد حمل:
مدارک ضروری برای حمل بین‌المللی کالا:
- بارنامه (Bill of Lading)
- فاکتور تجاری
- پکینگ لیست
- گواهی مبدا
برای ترخیص و تحویل کالا الزامی‌اند.
        """
    elif "اینکوترمز" in text:
        msg = """
📦 اینکوترمز:
قوانین بین‌المللی تخصیص هزینه و ریسک بین خریدار و فروشنده:
- EXW، FOB، CIF، DDP و ...
        """
    elif "ثبت سفارش" in text:
        msg = """
📝 ثبت سفارش:
مراحل:
1. دریافت پیش‌فاکتور
2. ثبت در سامانه جامع تجارت
3. اخذ مجوزها
4. تخصیص ارز
5. دریافت کد رهگیری ثبت سفارش
        """
    elif "ترخیص" in text:
        msg = """
🚛 ترخیص کالا:
1. اظهار کالا در سامانه EPL
2. بررسی کارشناسی
3. پرداخت هزینه‌ها
4. ارزیابی، بازرسی و مجوز خروج
        """
    elif "بازگشت" in text:
        return await show_menu(update)
    else:
        msg = "❌ لطفاً از گزینه‌های منوی آموزشی انتخاب کنید."
    await update.message.reply_text(msg)
    return EDU_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 عملیات لغو شد. برای شروع مجدد /start را وارد کنید."
    )
    return ConversationHandler.END


if __name__ == "__main__":
    print("🤖 Bot is running...")
    TOKEN = "8108601920:AAGImSZ8Jst_6lLT9x7FaYm1KvnITqpaJC8"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_option)],
            SELECT_CURRENCY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_currency)
            ],
            ARZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_arz)],
            FOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fob)],
            BIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bime)],
            HAMl: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_haml)],
            MAKHAZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_makhaz)],
            PASMAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pasmand)],
            EDU_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, education_menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
