import asyncio
import logging
from typing import Any
from queries.users import (
    get_distinct_subs_for_checker,
    get_domain_subscriptions,
)
from checker.const import (
    KDMID_TEMPLATE,
    QUEUE_TIMEOUT,
    SPAM_LIMIT,
    SPAM_TIMEOUT,
)
from checker.web import selenium_check_slots


def check_queue_wrapper(app: Any) -> None:
    asyncio.run(check_queue(app))


async def check_queue(app: Any) -> None:
    while True:
        await asyncio.sleep(QUEUE_TIMEOUT)
        subs = get_distinct_subs_for_checker()
        for sub in subs:
            domain = sub[0]
            found = check_slots(domain, sub[1], sub[2], sub[3])
            if found:
                await spam_if_found(domain, app)
            else:
                logger = logging.getLogger(__name__)
                logger.info(f'Not found for {domain}')


async def spam_if_found(domain: str, app: Any) -> None:
    domain_subs = get_domain_subscriptions(domain)
    for i in range(0, len(domain_subs), SPAM_LIMIT):
        await asyncio.sleep(SPAM_TIMEOUT)
        for j in range(i + 1):
            sub = domain_subs[j]
            url = KDMID_TEMPLATE.format(
                sub[3], sub[4], sub[5], sub[6]
            )
            await app.bot.send_message(
                chat_id=sub[1],
                text=f'🎉 Нашлись слоты в {sub[2]}. Для записи жми сюда: {url}'
            )


def check_slots(domain: str, id: int, code: str, ems: str) -> bool:
    return selenium_check_slots(KDMID_TEMPLATE.format(domain, id, code, ems))
