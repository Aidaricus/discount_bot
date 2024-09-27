import functools

from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram import Bot, Update, ParseMode
import logging

import keyboards
import scrapper
import keyboards
from config import TOKEN
from scrapper import urls
from content_maker import keyword_content

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update : Update, context : CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Приветствую в боте поиска скидок!🤑\n"
                                    f"Доступные сайты: {' '.join(urls.keys())} \n"
                                    f"Чтобы получить список скидок - /discount\n"
                                    "Как работает бот? - /help"
                             )

def discount(update : Update, context : CallbackContext):
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = 'Сайт выбран. Выбери режим поиска скидок',
        reply_markup = keyboards.get_discount_mode_keyboard()
    )

def keyword_search(update : Update, context : CallbackContext):
    user_data = context.user_data
    logging.info("user choose find using keyword mode")
    user_data = context.user_data
    user_data['asked-keyword'] = 1
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = 'Напиши ключевое слово по которому я должен искать:'
    )
def keyword_handler(update : Update, context : CallbackContext):
    user_data = context.user_data
    logging.info(f"Message handler detected message with text {update.message.text}")
    if (user_data['asked-keyword'] == 1):
        logging.info("Detected message is used like keyword")
        user_data['keyword'] = update.message.text
        user_data['asked-keyword'] = 0
        return send_list_content(update, context, keyword_content(user_data['site'], user_data['keyword']))
    logging.info("Detected message didn't use this message")
def show_discount_list(update : Update, context : CallbackContext):
    user_data = context.user_data
    logging.info("trying delete 6 messages after going to main menu")
    try:
        # Удаляем 10 сообщений для paginator'a
        for i in range(6):
            context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=user_data['message_ids']['message_ids'][i]
            )
        # Удаляем сообщение для reply_markup
        context.bot.delete_message(update.effective_chat.id, user_data['message_ids']['last_message_id'])
        logging.info("user_data['message_ids'] is defined")
    except:
        logging.info("user_data['message_ids'] already deleted")
        pass

    sites = list(urls.keys())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Приветствую ценителей денег!🤑\n"
                                  f"Доступные сайты: {' '.join(urls.keys())}\n. "
                                  f"Чтобы получить список скидок, выберите сайт с которого хотите получить информацию",
                             reply_markup = keyboards.get_sites_keyboard(sites)
                             )

def help(update : Update, context : CallbackContext):
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "<b>О боте:</b>\n"
               " <b><i>DiscountBot</i></b> - это бот который собирает данные о скидочных товарах с популярных сайтов одежды. Выводит их название цены и ссылку на них. \n\n"
               "<b>/discount</b> - основная функция бота. Бот выводит сообщения с информацией о товарах. Так как товаров может быть много, у бота есть удобный paginator"
               ", c помощью него вы можете листать этот список. Вся информация получается мгновенно из сайта. Используется технология веб-скраппинга, "
               "все цены актуальные на момент произведения скраппинга."
        ,
        parse_mode = ParseMode.HTML
    )

def send_list_content(update : Update, context : CallbackContext, content):

    if len(content['content_list']) == 0:
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Похоже таких скидок на сайте пока нет 😭",
            reply_markup = keyboards.get_retry_keyboard()
        )
    else:
        user_data = context.user_data

        logging.info(f"scrapper found {len(content['content_list'])} products in file content")

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Показываю список продуктов со следующим фильтром: {content["content_title"]}. '
                                      f'Вы можете листать список с помощью клавиатуры')

        user_data['page'] = 1
        user_data['content'] = content
        max_pages = len(content['content_list']) // 6
        if max_pages == 0: max_pages += 1
        message_ids  = {'last_message_id': None, 'message_ids' : []}
        cnt = 0
        for product in content["content_list"][0 : 6]:
            cnt += 1
            message_ids['message_ids'].append(
                context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text=f'{product["title"]}\n'
                         f'<s>{product["old_price"]}</s>. Новая цена: <b>{product["new_price"]}</b>\n'
                         f'{product["link"]}',
                    parse_mode = ParseMode.HTML

                ).message_id
            )

        message_ids['last_message_id'] = context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f'Страница № {user_data["page"]}',
            reply_markup = keyboards.get_paginator_keyboard(1, max_pages)
        ).message_id

        user_data['message_ids'] = message_ids

def paginator(update : Update, context : CallbackContext):
    user_data = context.user_data

    content = user_data['content']
    page = user_data['page']
    chat_id = update.effective_chat.id
    count_pages = len(content["content_list"])
    max_pages = count_pages // 6
    if max_pages == 0: max_pages = 1
    message_ids = user_data['message_ids']
    for i in range(6):
        product_info = content["content_list"][page * 6 + i]
        context.bot.edit_message_text(
            text = f'{product_info["title"]}\n'
                   f'<s>{product_info["old_price"]}</s>. Новая цена: <b>{product_info["new_price"]}</b>\n'
                   f'{product_info["link"]}\n',
            chat_id = chat_id,
            message_id = message_ids['message_ids'][i],
            parse_mode = ParseMode.HTML
        )

    context.bot.edit_message_text(
        text=f'Страница № {page}',
        chat_id=chat_id,
        message_id=user_data['message_ids']['last_message_id']
    )

    context.bot.edit_message_reply_markup(
        reply_markup = keyboards.get_paginator_keyboard(page, max_pages),
        chat_id = chat_id,
        message_id = user_data['message_ids']['last_message_id']
    )

def keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith('paginator'):
        return paginator_keyboard_handler(update, context, data)
    elif data.startswith('choose_site'):
        return discount_keyboard_handler(update, context, data)
    elif data == 'retry_asos':
        return send_list_content(update, context, scrapper.scrap(context.user_data['site']))
    elif data.startswith('mode'):
        return mode_keyboard_handler(update, context, data)

def mode_keyboard_handler(update : Update, context : CallbackContext, data):
    if data == "mode-clear-list":
        return send_list_content(update, context, scrapper.scrap(context.user_data['site']))
    elif data == "mode-keyword":
        return keyword_search(update, context)

def paginator_keyboard_handler(update : Update, context : CallbackContext, data):
    if data == "paginator_next":
        context.user_data['page'] += 1
        return paginator(update, context)
    elif data == "paginator_prev":
        if (context.user_data['page'] == 1):
            print("пытается пойти в отрицательную страницу")
            return paginator(update, context)
        context.user_data['page'] -= 1
        return paginator(update, context)
    elif data == "paginator_back":
        return show_discount_list(update, context)

def discount_keyboard_handler(update : Update, context : CallbackContext, data):
    if data == "choose_site_asos":
        context.user_data['site'] = 'asos'
    elif data == "choose_site_lamoda":
        context.user_data['site'] = 'lamoda'
        # return send_list_content(update, context, "lamoda")
    return discount(update, context)

def main():
    bot = Bot(token = TOKEN)
    updater = Updater(bot = bot, use_context = True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("discount", show_discount_list))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CallbackQueryHandler(callback=keyboard_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, callback=keyword_handler))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
