import logging
import asyncio
import re
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

SUB_DATA = 1
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
        "Пожалуйста, предоставь ссылку из посольства вида: https://belgrad.kdmid.ru/queue/orderinfo.aspx?id=75490&cd=d645e055&ems=97BF4526"
    )
    return SUB_DATA


async def create_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    u_input = update.message.text
    names = get_countries_names()
    country = u_input.split(".")[0].strip("http://").strip("https://")
    if country not in names:
        await update.message.reply_text(
            "Такого города пока нет, может, cкоро добавим!",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=update.message.id,
        )
        return SUB_DATA
    
    id = re.search(r'id=[0-9]{5}', u_input)
    if id is None:
        await update.message.reply_text(
            "Кривой ID (&id=) :(",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=update.message.id,
        )
        return SUB_DATA
    id = id.group().split("=")[1]

    code = re.search(r'cd=[a-z0-9]{8}', u_input)
    if code is None:
        await update.message.reply_text(
            "Не очень похоже на валидный код (&cd=) :(",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=update.message.id,
        )
        return SUB_DATA
    code = code.group().split("=")[1]

    ems = re.search(r'ems=[A-Z0-9]{8}', u_input)
    if ems is None:
        await update.message.reply_text(
            "Какой-то неправильный EMS (&ems=) :(",
            reply_markup=ReplyKeyboardRemove(),
            reply_to_message_id=update.message.id,
        )
        return SUB_DATA
    ems = ems.group().split("=")[1]
    create_user({
        'user_id': update.message.from_user.id,
        'country': names[country],
        'country_url': country,
        'number': id,
        'code': code,
        'ems': ems,
    })
    await update.message.reply_text(
        "Готово! Подписка создана.\n\n"
        "Чтобы посмотреть свои подписки, используй /subscriptions",
        reply_to_message_id=update.message.id,
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
            f"Твои подписки:\n\n{'\n'.join(p_subs)}",
            reply_to_message_id=update.message.id,
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )


async def cities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    names = get_countries_names()
    available_cities = [
        f"*{names[s].replace('-', '\-').strip()}*: {s} в ссылке"
        for s in names
    ]
    await update.message.reply_text(
        f"Доступные города:\n\n{'\n'.join(available_cities)}",
        reply_to_message_id=update.message.id,
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    names_mapping = get_countries_names()
    subs = get_user_subscriptions(user.id)
    reply_keyboard = [[names_mapping[sub[3]] for sub in subs]]
    await update.message.reply_text(
        "Начнем оформление отписки!\n\n"
        "Выбери подписку в каком городе ты хочешь отменить.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select a country"
        ),
    )
    return SUB_ID


async def delete_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    names_mapping = get_countries_names()
    subs = get_user_subscriptions(user.id)
    proper_user_names = [names_mapping[sub[3]] for sub in subs]
    if update.message.text not in proper_user_names:
        await update.message.reply_text(
            "Такой подписки у тебя нет!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SUB_ID
    delete_user_subscription(update.message.from_user.id, update.message.text)
    await update.message.reply_text(
        f"Успешно отписался от {update.message.text}!",
        reply_markup=ReplyKeyboardRemove(),
    )
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
            SUB_DATA: [MessageHandler(filters.TEXT, create_subscription)],
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
    application.add_handler(CommandHandler("cities", cities))

    application.add_handler(subscribe_handler)
    application.add_handler(unsubscribe_handler)
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    pool.submit(check_queue_wrapper, application)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
   main()
