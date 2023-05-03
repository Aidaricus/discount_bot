from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

import scrapper
from keyboards import get_paginator_keyboard, get_sites_keyboard, get_retry_keyboard
from config import TOKEN
from scrapper import urls


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update : Update, context : CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Приветствую в боте поиска скидок!🤑\n"
                                    f"Доступные сайты: {''.join(urls.keys())} \nЧтобы получить список - /discount\n"
                                    "Как работает бот? - /help"
                             )

def discount(update : Update, context : CallbackContext):
    sites = list(urls.keys())
    print(sites)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Приветствую ценителей денег!🤑\n"
                                  "Доступные сайты: asos.com\n Чтобы получить список скидок, выберите сайт с которого хотите получить информацию",
                             reply_markup = get_sites_keyboard(sites)
                             )

def help(update : Update, context : CallbackContext):
    context.bot.send_message(chat_id = update.effective_chat.id,
                             text = "Вы серьезно? Пока только одна функция, что непонятного в том чтобы просто нажать "
                                    "/discount???")

def send_list_content(update : Update, context : CallbackContext, site):
    content = scrapper.scrap(site)

    if len(content['content_list']) == 0:
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Сори не получилось соскрапить с сайта asos.com из за их блока. Попробуйте ещё раз, скраппинг получается через 1-2 попытки.",
            reply_markup = get_retry_keyboard()
        )
    else:
        logging.info(f"scrapper found {len(content['content_list'])} products in file content/")

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Показываю список продуктов со следующим фильтром: {content["content_title"]}. '
                                      f'Вы можете листать список с помощью клавиатуры')

        user_data = context.user_data
        user_data['page'] = 1
        user_data['content'] = content

        message_ids  = {'last_message_id': None, 'message_ids' : []}
        cnt = 0
        for product in content["content_list"][0 : 10]:
            cnt += 1
            message_ids['message_ids'].append(
                context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text=f'{product["title"]}\n'
                         f'{product["price"]}\n'
                         f'{product["link"]}'
                ).message_id
            )

        message_ids['last_message_id'] = context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f'Страница № {user_data["page"]}',
            reply_markup = get_paginator_keyboard(1, len(content['content_list']) // 10)
        ).message_id

        user_data['message_ids'] = message_ids

def paginator(update : Update, context : CallbackContext):
    user_data = context.user_data

    content = user_data['content']
    page = user_data['page']
    chat_id = update.effective_chat.id
    count_pages = len(content["content_list"])
    max_pages = count_pages // 10
    message_ids = user_data['message_ids']
    for i in range(10):
        product_info = content["content_list"][page * 10 + i]
        context.bot.edit_message_text(
            text = f'{product_info["title"]}\n'
                   f'{product_info["price"]}\n'
                   f'{product_info["link"]}\n',
            chat_id = chat_id,
            message_id = message_ids['message_ids'][i]
        )

    context.bot.edit_message_text(
        text=f'Страница № {page}',
        chat_id=chat_id,
        message_id=user_data['message_ids']['last_message_id']
    )

    context.bot.edit_message_reply_markup(
        reply_markup = get_paginator_keyboard(page, max_pages),
        chat_id = chat_id,
        message_id = user_data['message_ids']['last_message_id']
    )

#TODO: 1) Сделать возможность выводить список страницами(реализовать клавиатурный переключатель между страницами)  DONE

def keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith('paginator'):
        return paginator_keyboard_handler(update, context, data)
    elif data.startswith('choose_site'):
        return discount_keyboard_handler(update, context, data)
    elif data == 'retry_asos':
        return send_list_content(update, context, "asos")

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
        return discount(update, context)

def discount_keyboard_handler(update : Update, context : CallbackContext, data):
    if data == "choose_site_asos":
        return send_list_content(update, context, "asos")
    elif data == "choose_site_lamoda":
        return send_list_content(update, context, "lamoda")


def main():
    bot = Bot(token = TOKEN)
    updater = Updater(bot = bot, use_context = True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("discount", discount))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CallbackQueryHandler(callback=keyboard_handler))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
