import logging
import asyncio
import concurrent.futures
from telegram import (
    ForceReply,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    constants
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from queries.countries import (
    get_countries_names,
)
from queries.users import (
    check_if_exists,
    create_user,
    update_user_value,
    get_user_subscriptions,
    delete_user_subscription,
)
from checker.checker import check_queue_wrapper


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

COUNTRIES, ID, CODE, EMS = range(4)
SUB_ID = 1


TOKEN = "6944279697:AAGIYdJrguNM8mqfVvtNyIxA38IJycqJfik"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Привет! Я здесь, чтобы помочь тебе поймать слот на запись на паспорт!. Я уведомлю тебя, когда по твоей заявке появятся свободные слоты.\n\n"
        "Чтобы подписаться на какое-либо из доступных консульств, используй /subscribe.\n\n"
        "Для оформления подписки понадобится ссылка, выданная в консульстве."
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [list(get_countries_names())]
    await update.message.reply_text(
        "Начнем оформление заявочки!\n\n"
        "Выбери желаемый город из возможного списка.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select a country"
        ),
    )
    return COUNTRIES


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Country of %s: %s", user.first_name, update.message.text)
    _id = check_if_exists(user.id, update.message.text)
    if _id is not None:
        await update.message.reply_text(
            "Такая подписка уже есть у тебя, попробуй другой город.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return COUNTRIES
    
    names = get_countries_names()
    if update.message.text not in names:
        await update.message.reply_text(
            "Такого города пока нет, может, cкоро добавим!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return COUNTRIES
    create_user(user.id, update.message.text, names[update.message.text])
    await update.message.reply_text(
        "Благодарю за выбор!",
        reply_to_message_id=update.message.id,
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_photo(
        photo="assets/pics/id.png",
        caption="Теперь потребуется идентификатор заявки из ссылки (рисунок подскажет).",
    )
    return ID


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Code of %s: %s", user.first_name, update.message.text)
    update_user_value(user.id, 'number', update.message.text)
    await update.message.reply_text(
        "Записал!",
        reply_to_message_id=update.message.id,
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_photo(
        photo="assets/pics/code.png",
        caption="Теперь потребуется код заявки из ссылки (рисунок подскажет).",
    )

    return CODE


async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Code of %s: %s", user.first_name, update.message.text)
    update_user_value(user.id, 'code', update.message.text)
    await update.message.reply_text(
        "Отлично!",
        reply_to_message_id=update.message.id,
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_photo(
        photo="assets/pics/ems.png",
        caption="Теперь потребуется код EMS из ссылки (рисунок подскажет).",
    )
    return EMS


async def get_ems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("EMS of %s: %s", user.first_name, update.message.text)
    update_user_value(user.id, 'ems', update.message.text)
    await update.message.reply_text(
        "Готово! Подписка создана.\n\n"
        "Чтобы посмотреть свои подписки, используй /subscriptions",
        reply_to_message_id=update.message.id,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    subs = get_user_subscriptions(user.id)
    p_subs = [f'*{s[2]}*' for s in subs]
    if len(p_subs) == 0:
        await update.message.reply_text(
            f"У тебя пока нет подписок :(",
            reply_to_message_id=update.message.id,
        )
    else:
        await update.message.reply_text(
            f"Твои подписки:\n {'\n'.join(p_subs)}",
            reply_to_message_id=update.message.id,
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [list(get_countries_names())]
    await update.message.reply_text(
        "Начнем оформление отписки!\n\n"
        "Выбери подписку в каком городе ты хочешь отменить.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select a country"
        ),
    )
    return SUB_ID


async def delete_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    names = get_countries_names()
    if update.message.text not in names:
        await update.message.reply_text(
            "Такой подписки у тебя нет!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SUB_ID
    delete_user_subscription(update.message.from_user.id, update.message.text)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    subscribe_handler = ConversationHandler(
        entry_points=[CommandHandler("subscribe", subscribe)],
        states={
            COUNTRIES: [MessageHandler(filters.Regex("^(Istanbul|Belgrade|hague)$"), get_country)],
            ID: [MessageHandler(filters.Regex("^[0-9]{5,6}$"), get_id)],
            CODE: [MessageHandler(filters.Regex("^[a-z0-9]{8}$"), get_code)],
            EMS: [MessageHandler(filters.Regex("^[A-Z0-9]{8}$"), get_ems)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    unsubscribe_handler = ConversationHandler(
        entry_points=[CommandHandler("unsubscribe", unsubscribe)],
        states={
            SUB_ID: [MessageHandler(filters.TEXT, delete_subscription)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscriptions", subscriptions))
    application.add_handler(subscribe_handler)
    application.add_handler(unsubscribe_handler)
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    pool.submit(check_queue_wrapper, application)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
   main()
