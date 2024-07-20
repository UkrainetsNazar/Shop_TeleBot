import app.keyboards as kb
from app.models import async_session, WomanCloth, ManCloth, AddCloth_Man, AddCloth_Woman
from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, KeyboardButton, InputMediaPhoto)
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
router = Router()
state = {}

man_navigation_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Замовити"), KeyboardButton(text="Далі➡️")],
                                                  [KeyboardButton(text="Назад")]],
                                        resize_keyboard=True,
                                        input_field_placeholder='Листайте каталог за допомогою стрілочок...')

woman_navigation_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🌷Замовити🌷"), KeyboardButton(text="🌷Далі➡️")],
                                                    [KeyboardButton(text="Назад")]],
                                          resize_keyboard=True,
                                          input_field_placeholder='Листайте каталог за допомогою стрілочок...')


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Вітаємо Вас у нашому магазині <b>SecondWave Wear</b>🌊\n\n '
                         'Щоб перейти в головне меню натисніть кнопку Меню.', parse_mode="HTML",
                         reply_markup=kb.menu)


@router.callback_query(F.data == 'Меню')
async def cmd_menu(callback: CallbackQuery):
    await callback.message.answer('Оберіть що саме вас цікавить:', reply_markup=kb.main)


@router.callback_query(F.data == 'Назад')
async def cmd_back_(callback: CallbackQuery):
    await callback.message.answer('Оберіть що саме вас цікавить:', reply_markup=kb.main)


@router.message(F.text == 'Назад')
async def cmd_back(message: Message):
    await message.answer("Повернення до головного меню...", reply_markup=ReplyKeyboardRemove())
    await message.answer('Оберіть що саме вас цікавить:', reply_markup=kb.main)


@router.callback_query(F.data == 'rules')
async def rules(callback: CallbackQuery):
    await callback.message.answer('Щоб закинути річ на продаж вам потрібно:\n'
                                  'Натиснути на кнопку <b>"Закинути річ на продаж"</b> та надіслати:\n'
                                  '🖇️Якісне фото(3-5шт.)\n 🖇️Бренд товару\n 🖇️Розмір\n 🖇️Вартість\n 🖇️Стан\n\n'
                                  'Також є можливість продажу через нашого гаранта:@tsukuyomitravel',
                                  reply_markup=kb.back, parse_mode="HTML")


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.message.answer('Оберіть стать на яку ви шукаєте річ:', reply_markup=kb.sex)


@router.callback_query(F.data == 'sale')
async def sale(callback: CallbackQuery):
    telegram_profile_link = "https://t.me/tsukuyomitravel"  # Replace 'yourusername' with your actual Telegram username
    await callback.message.answer(f'Щоб продати річ пишіть <a href="{telegram_profile_link}">сюди</a>',
                                  parse_mode="HTML")


async def display_item(callback_or_message, item, navigation_kb):
    photos = [item.фото1, item.фото2, item.фото3, item.фото4, item.фото5]
    photos = [photo for photo in photos if photo]

    if photos:
        media_group = [InputMediaPhoto(media=photo) for photo in photos]
        text = f"Бренд: {item.бренд}\nРозмір: {item.розмір}\nВартість: {item.вартість} грн\nСтан: {item.стан}/10\n"
        media_group[0].caption = text
    else:
        media_group = [InputMediaPhoto(media='', caption=f"Бренд: {item.бренд}\nРозмір: {item.розмір}\nВартість: {item.вартість} грн\nСтан: {item.стан}/10\n")]

    user_state = state[callback_or_message.from_user.id]
    user_state['current_item'] = item

    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.answer_media_group(media=media_group)
        await callback_or_message.message.answer("Обирайте наступні дії:", reply_markup=navigation_kb)
    else:
        await callback_or_message.answer_media_group(media=media_group)
        await callback_or_message.answer("Обирайте наступні дії:", reply_markup=navigation_kb)


@router.callback_query(F.data == 'man')
async def show_men_clothes(callback: CallbackQuery):
    state[callback.from_user.id] = {'type': 'man', 'index': 0}
    await display_next_item(callback)


@router.callback_query(F.data == 'woman')
async def show_women_clothes(callback: CallbackQuery):
    state[callback.from_user.id] = {'type': 'woman', 'index': 0}
    await display_next_item(callback)


@router.message(F.text == "Далі➡️")
async def next_item(message: Message):
    if message.from_user.id in state:
        state[message.from_user.id]['index'] += 1
        await display_next_item(message)


@router.message(F.text == "🌷Далі➡️")
async def next_item_woman(message: Message):
    if message.from_user.id in state:
        state[message.from_user.id]['index'] += 1
        await display_next_item(message)


async def display_next_item(callback_or_message):
    user_state = state[callback_or_message.from_user.id]
    index = user_state['index']
    item_type = user_state['type']

    async with async_session() as session:
        if item_type == 'man':
            result = await session.execute(select(ManCloth).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = man_navigation_kb
        else:
            result = await session.execute(select(WomanCloth).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = woman_navigation_kb

        if items:
            await display_item(callback_or_message, items[0], navigation_kb)
        else:
            await callback_or_message.answer("Немає більше товарів у цій категорії.")


@router.message(F.text == "Замовити")
async def order_item(message: Message):
    user_state = state.get(message.from_user.id)
    if user_state and 'current_item' in user_state:
        item = user_state['current_item']
        if hasattr(item, 'tg_link') and item.tg_link:
            await message.answer(f"Для замовлення цієї речі, зв'яжіться з продавцем: {item.tg_link}")
        else:
            await message.answer("На жаль, для цієї речі не вказано контактну інформацію.")
    else:
        await message.answer("Не вдалося знайти інформацію про обраний товар.")



@router.message(F.text == "🌷Замовити🌷")
async def order_item_woman(message: Message):
    user_state = state.get(message.from_user.id)
    if user_state and 'current_item' in user_state:
        item = user_state['current_item']
        if hasattr(item, 'tg_link') and item.tg_link:
            await message.answer(f"Для замовлення цієї речі, зв'яжіться з продавцем: {item.tg_link}")
        else:
            await message.answer("На жаль, для цієї речі не вказано контактну інформацію.")
    else:
        await message.answer("Не вдалося знайти інформацію про обраний товар.")


@router.message(Command('add_cloth_to_my_DB'))
async def add_cloth(message: Message):
    await message.answer("Оберіть стать до якої ви хочете додати річ:",reply_markup=kb.sex_admin)


@router.message(F.text == 'add_man_cloth')
async def set_state(message: Message, state: FSMContext):
    await state.set_state(AddCloth_Man.бренд)
    await message.answer("Введіть назву бренду:")


@router.message(AddCloth_Man.бренд)
async def add_brand(message: Message, state: FSMContext):
    await state.update_data(бренд=message.text)
    await state.set_state(AddCloth_Man.розмір)
    await message.answer("Введіть розмір одягу:")


@router.message(AddCloth_Man.розмір)
async def add_size(message: Message, state: FSMContext):
    await state.update_data(розмір=message.text)
    await state.set_state(AddCloth_Man.вартість)
    await message.answer("Введіть вартість одягу:")


@router.message(AddCloth_Man.вартість)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(вартість=message.text)
    await state.set_state(AddCloth_Man.стан)
    await message.answer("Введіть стан одягу:")


@router.message(AddCloth_Man.стан)
async def add_stan(message: Message, state: FSMContext):
    await state.update_data(стан=message.text)
    await state.set_state(AddCloth_Man.tg_link)
    await message.answer("Введіть tg_link продавця:")


#Додати функцію яка приймає фото і функцію яка заносить цю річ у бд