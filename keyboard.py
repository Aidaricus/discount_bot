from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_paginator_keyboard(page, max_pages):
    keyboard = [
        [
            InlineKeyboardButton('◀️Назад', callback_data='paginator_prev'),
            InlineKeyboardButton(f'{page}/{max_pages}', callback_data='_none'),
            InlineKeyboardButton('Вперед▶️', callback_data='paginator_next'),
        ]
    ]
    keyboard.append([InlineKeyboardButton('Вернуться в главное меню↩️', callback_data='paginator_back')])
    return InlineKeyboardMarkup(keyboard)

def get_discount_mode_keyboard():
    keyboard = [
        [InlineKeyboardButton('Без фильтров🍃', callback_data='mode-clear-list'),
         InlineKeyboardButton('По ключевому слову', callback_data='mode-keyword')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sites_keyboard(sites):
    keyboard = [[]]
    for site in sites:
        keyboard[0].append(InlineKeyboardButton(f'Искать на {site}', callback_data = f'choose_site_{site}'))
    return InlineKeyboardMarkup(keyboard)
def get_retry_keyboard():
    keyboard = [[InlineKeyboardButton('Попробовать ещё раз 🔁', callback_data= "retry_asos")]]
    return InlineKeyboardMarkup(keyboard)
