from aiogram.types import (InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)



main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔍Каталог🔍', callback_data='catalog')],
    [InlineKeyboardButton(text='📩Закинути річ на продаж📩', callback_data='sale')],
    [InlineKeyboardButton(text='📝Правила📝', callback_data='rules')]])

menu = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton (text='Меню', callback_data='Меню')]])

back = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton (text='Назад', callback_data='Назад')]])

sex = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Чоловічий♂️', callback_data='man'),
     InlineKeyboardButton(text='Жіночий♀️', callback_data='woman')]])

sex_admin = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='add_man_cloth'),
                                          KeyboardButton(text='add_woman_cloth')]], resize_keyboard=True)

man_navigation_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Замовити"), KeyboardButton(text="Далі➡️")],
                                                  [KeyboardButton(text="Назад")]],
                                        resize_keyboard=True,
                                        input_field_placeholder='Листайте каталог за допомогою стрілочок...')

woman_navigation_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🌷Замовити🌷"), KeyboardButton(text="🌷Далі➡️")],
                                                    [KeyboardButton(text="Назад")]],
                                          resize_keyboard=True,
                                          input_field_placeholder='Листайте каталог за допомогою стрілочок...')


skip_photo_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустити")]],
    resize_keyboard=True
)