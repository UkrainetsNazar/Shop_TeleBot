import app.keyboards as kb
from app.models import (async_session, WomanCloth, ManCloth, AddCloth_Man, AddCloth_Woman,
                        ManShoes, WomanShoes, AddShoes_Man, AddShoes_Woman)

from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery,
                           ReplyKeyboardRemove, InputMediaPhoto)
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
router = Router()
state = {}


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
        text = f"Бренд: {item.бренд}\nРозмір: {item.розмір}\nВартість: {item.вартість}\nСтан: {item.стан}/10\n"
        media_group[0].caption = text
    else:
        media_group = [InputMediaPhoto(media='', caption=f"Бренд: {item.бренд}\nРозмір: {item.розмір}\nВартість: {item.вартість}\nСтан: {item.стан}/10\n")]

    user_state = state[callback_or_message.from_user.id]
    user_state['current_item'] = item

    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.answer_media_group(media=media_group)
        await callback_or_message.message.answer("Обирайте наступні дії:", reply_markup=navigation_kb)
    else:
        await callback_or_message.answer_media_group(media=media_group)
        await callback_or_message.answer("Обирайте наступні дії:", reply_markup=navigation_kb)


@router.callback_query(F.data == 'man')
async def choose_item_man(callback: CallbackQuery):
    await callback.message.answer('Оберіть категорію:',reply_markup=kb.choose_item_man)


@router.callback_query(F.data == 'man_cloth')
async def show_men_clothes(callback: CallbackQuery):
    state[callback.from_user.id] = {'type': 'man', 'index': 0}
    await display_next_item(callback)


@router.callback_query(F.data == 'man_shoes')
async def show_men_shoes(callback: CallbackQuery):
    state[callback.from_user.id] = {'type': 'man_shoes', 'index': 0}
    await display_next_item(callback)


@router.callback_query(F.data == 'woman_shoes')
async def show_women_shoes(callback: CallbackQuery):
    state[callback.from_user.id] = {'type': 'woman_shoes', 'index': 0}
    await display_next_item(callback)


@router.callback_query(F.data == 'woman')
async def choose_item_woman(callback: CallbackQuery):
    await callback.message.answer('Оберіть категорію:',reply_markup=kb.choose_item_woman)


@router.callback_query(F.data == 'woman_cloth')
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
            result = await session.execute(select(ManCloth).order_by(ManCloth.id.desc()).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = kb.man_navigation_kb
        elif item_type == 'woman':
            result = await session.execute(select(WomanCloth).order_by(WomanCloth.id.desc()).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = kb.woman_navigation_kb
        elif item_type == 'man_shoes':
            result = await session.execute(select(ManShoes).order_by(ManShoes.id.desc()).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = kb.man_shoes_navigation_kb
        elif item_type == 'woman_shoes':
            result = await session.execute(select(WomanShoes).order_by(WomanShoes.id.desc()).offset(index).limit(1))
            items = result.scalars().all()
            navigation_kb = kb.woman_shoes_navigation_kb

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


@router.message(F.text == "Замовити взуття")
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


@router.message(F.text == "🌷Замовити взуття🌷")
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


async def save_cloth_to_db(state: FSMContext, cloth_model):
    data = await state.get_data()
    async with async_session() as session:
        new_cloth = cloth_model(
            бренд=data.get('бренд'),
            розмір=data.get('розмір'),
            вартість=data.get('вартість'),
            стан=data.get('стан'),
            фото1=data.get('фото1'),
            фото2=data.get('фото2'),
            фото3=data.get('фото3'),
            фото4=data.get('фото4'),
            фото5=data.get('фото5'),
            tg_link=data.get('tg_link')
        )
        session.add(new_cloth)
        await session.commit()


@router.message(Command('add_cloth_to_my_DB'))
async def add_cloth(message: Message):
    await message.answer("Оберіть стать до якої ви хочете додати річ:",reply_markup=kb.sex_admin)


@router.message(F.text == 'add_man_item')
async def set_state(message: Message):
    await message.answer("Оберіть категорію:",reply_markup=kb.sex_category_man)


@router.message(F.text == 'add_woman_item')
async def set_state(message: Message):
    await message.answer("Оберіть категорію:",reply_markup=kb.sex_category_woman)


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
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(стан=message.text)
    await state.set_state(AddCloth_Man.фото1)
    await message.answer("Надішліть перше фото одягу:")


@router.message(AddCloth_Man.фото1, F.photo)
async def add_photo1(message: Message, state: FSMContext):
    await state.update_data(фото1=message.photo[-1].file_id)
    await state.set_state(AddCloth_Man.фото2)
    await message.answer("Надішліть друге фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Man.фото2, F.photo)
async def add_photo2(message: Message, state: FSMContext):
    await state.update_data(фото2=message.photo[-1].file_id)
    await state.set_state(AddCloth_Man.фото3)
    await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Man.фото3, F.photo)
async def add_photo3(message: Message, state: FSMContext):
    await state.update_data(фото3=message.photo[-1].file_id)
    await state.set_state(AddCloth_Man.фото4)
    await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Man.фото4, F.photo)
async def add_photo4(message: Message, state: FSMContext):
    await state.update_data(фото4=message.photo[-1].file_id)
    await state.set_state(AddCloth_Man.фото5)
    await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Man.фото5, F.photo)
async def add_photo5(message: Message, state: FSMContext):
    await state.update_data(фото5=message.photo[-1].file_id)
    await state.set_state(AddCloth_Man.tg_link)
    await message.answer("Введіть tg_link продавця:",reply_markup=ReplyKeyboardRemove())


@router.message(AddCloth_Man.tg_link)
async def add_tg_link(message: Message, state: FSMContext):
    await state.update_data(tg_link=message.text)
    await save_cloth_to_db(state, ManCloth)
    await state.clear()
    await message.answer("Чоловічий одяг успішно додано до бази даних.", reply_markup=kb.menu)

@router.message(F.text == 'add_woman_cloth')
async def set_state(message: Message, state: FSMContext):
    await state.set_state(AddCloth_Woman.бренд)
    await message.answer("Введіть назву бренду:")


@router.message(AddCloth_Woman.бренд)
async def add_brand(message: Message, state: FSMContext):
    await state.update_data(бренд=message.text)
    await state.set_state(AddCloth_Woman.розмір)
    await message.answer("Введіть розмір одягу:")


@router.message(AddCloth_Woman.розмір)
async def add_size(message: Message, state: FSMContext):
    await state.update_data(розмір=message.text)
    await state.set_state(AddCloth_Woman.вартість)
    await message.answer("Введіть вартість одягу:")


@router.message(AddCloth_Woman.вартість)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(вартість=message.text)
    await state.set_state(AddCloth_Woman.стан)
    await message.answer("Введіть стан одягу:")


@router.message(AddCloth_Woman.стан)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(стан=message.text)
    await state.set_state(AddCloth_Woman.фото1)
    await message.answer("Надішліть перше фото одягу:")


@router.message(AddCloth_Woman.фото1, F.photo)
async def add_photo1(message: Message, state: FSMContext):
    await state.update_data(фото1=message.photo[-1].file_id)
    await state.set_state(AddCloth_Woman.фото2)
    await message.answer("Надішліть друге фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Woman.фото2, F.photo)
async def add_photo2(message: Message, state: FSMContext):
    await state.update_data(фото2=message.photo[-1].file_id)
    await state.set_state(AddCloth_Woman.фото3)
    await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Woman.фото3, F.photo)
async def add_photo3(message: Message, state: FSMContext):
    await state.update_data(фото3=message.photo[-1].file_id)
    await state.set_state(AddCloth_Woman.фото4)
    await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Woman.фото4, F.photo)
async def add_photo4(message: Message, state: FSMContext):
    await state.update_data(фото4=message.photo[-1].file_id)
    await state.set_state(AddCloth_Woman.фото5)
    await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddCloth_Woman.фото5, F.photo)
async def add_photo5(message: Message, state: FSMContext):
    await state.update_data(фото5=message.photo[-1].file_id)
    await state.set_state(AddCloth_Woman.tg_link)
    await message.answer("Введіть tg_link продавця:",reply_markup=ReplyKeyboardRemove())


@router.message(AddCloth_Woman.tg_link)
async def add_tg_link(message: Message, state: FSMContext):
    await state.update_data(tg_link=message.text)
    await save_cloth_to_db(state, WomanCloth)
    await state.clear()
    await message.answer("Жіночий одяг успішно додано до бази даних.", reply_markup=kb.menu)


@router.message(F.text == 'Пропустити')
async def skip_photo(message: Message, state: FSMContext):
    user_state = await state.get_state()
    if user_state == AddCloth_Man.фото2:
        await state.set_state(AddCloth_Man.фото3)
        await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Man.фото3:
        await state.set_state(AddCloth_Man.фото4)
        await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Man.фото4:
        await state.set_state(AddCloth_Man.фото5)
        await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Man.фото5:
        await state.set_state(AddCloth_Man.tg_link)
        await message.answer("Введіть tg_link продавця:", reply_markup=ReplyKeyboardRemove())

    elif user_state == AddCloth_Woman.фото2:
        await state.set_state(AddCloth_Woman.фото3)
        await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Woman.фото3:
        await state.set_state(AddCloth_Woman.фото4)
        await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Woman.фото4:
        await state.set_state(AddCloth_Woman.фото5)
        await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddCloth_Woman.фото5:
        await state.set_state(AddCloth_Woman.tg_link)
        await message.answer("Введіть tg_link продавця:", reply_markup=ReplyKeyboardRemove())

    elif user_state == AddShoes_Man.фото2:
        await state.set_state(AddShoes_Man.фото3)
        await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Man.фото3:
        await state.set_state(AddShoes_Man.фото4)
        await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Man.фото4:
        await state.set_state(AddShoes_Man.фото5)
        await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Man.фото5:
        await state.set_state(AddShoes_Man.tg_link)
        await message.answer("Введіть tg_link продавця:", reply_markup=ReplyKeyboardRemove())

    elif user_state == AddShoes_Woman.фото2:
        await state.set_state(AddShoes_Woman.фото3)
        await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Woman.фото3:
        await state.set_state(AddShoes_Woman.фото4)
        await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Woman.фото4:
        await state.set_state(AddShoes_Woman.фото5)
        await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):", reply_markup=kb.skip_photo_kb)
    elif user_state == AddShoes_Woman.фото5:
        await state.set_state(AddShoes_Woman.tg_link)
        await message.answer("Введіть tg_link продавця:", reply_markup=ReplyKeyboardRemove())



@router.message(F.text == 'add_man_shoes')
async def set_state(message: Message, state: FSMContext):
    await state.set_state(AddShoes_Man.бренд)
    await message.answer("Введіть назву бренду:")


@router.message(AddShoes_Man.бренд)
async def add_brand(message: Message, state: FSMContext):
    await state.update_data(бренд=message.text)
    await state.set_state(AddShoes_Man.розмір)
    await message.answer("Введіть розмір взуття:")


@router.message(AddShoes_Man.розмір)
async def add_size(message: Message, state: FSMContext):
    await state.update_data(розмір=message.text)
    await state.set_state(AddShoes_Man.вартість)
    await message.answer("Введіть вартість взуття:")


@router.message(AddShoes_Man.вартість)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(вартість=message.text)
    await state.set_state(AddShoes_Man.стан)
    await message.answer("Введіть стан взуття:")


@router.message(AddShoes_Man.стан)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(стан=message.text)
    await state.set_state(AddShoes_Man.фото1)
    await message.answer("Надішліть перше фото взуття:")


@router.message(AddShoes_Man.фото1, F.photo)
async def add_photo1(message: Message, state: FSMContext):
    await state.update_data(фото1=message.photo[-1].file_id)
    await state.set_state(AddShoes_Man.фото2)
    await message.answer("Надішліть друге фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Man.фото2, F.photo)
async def add_photo2(message: Message, state: FSMContext):
    await state.update_data(фото2=message.photo[-1].file_id)
    await state.set_state(AddShoes_Man.фото3)
    await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Man.фото3, F.photo)
async def add_photo3(message: Message, state: FSMContext):
    await state.update_data(фото3=message.photo[-1].file_id)
    await state.set_state(AddShoes_Man.фото4)
    await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Man.фото4, F.photo)
async def add_photo4(message: Message, state: FSMContext):
    await state.update_data(фото4=message.photo[-1].file_id)
    await state.set_state(AddShoes_Man.фото5)
    await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Man.фото5, F.photo)
async def add_photo5(message: Message, state: FSMContext):
    await state.update_data(фото5=message.photo[-1].file_id)
    await state.set_state(AddShoes_Man.tg_link)
    await message.answer("Введіть tg_link продавця:",reply_markup=ReplyKeyboardRemove())


@router.message(AddShoes_Man.tg_link)
async def add_tg_link(message: Message, state: FSMContext):
    await state.update_data(tg_link=message.text)
    await save_cloth_to_db(state, ManShoes)
    await state.clear()
    await message.answer("Чоловіче взуття успішно додано до бази даних.", reply_markup=kb.menu)


@router.message(F.text == 'add_woman_shoes')
async def set_state(message: Message, state: FSMContext):
    await state.set_state(AddShoes_Woman.бренд)
    await message.answer("Введіть назву бренду:")


@router.message(AddShoes_Woman.бренд)
async def add_brand(message: Message, state: FSMContext):
    await state.update_data(бренд=message.text)
    await state.set_state(AddShoes_Woman.розмір)
    await message.answer("Введіть розмір взуття:")


@router.message(AddShoes_Woman.розмір)
async def add_size(message: Message, state: FSMContext):
    await state.update_data(розмір=message.text)
    await state.set_state(AddShoes_Woman.вартість)
    await message.answer("Введіть вартість взуття:")


@router.message(AddShoes_Woman.вартість)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(вартість=message.text)
    await state.set_state(AddShoes_Woman.стан)
    await message.answer("Введіть стан взуття:")


@router.message(AddShoes_Woman.стан)
async def add_cost(message: Message, state: FSMContext):
    await state.update_data(стан=message.text)
    await state.set_state(AddShoes_Woman.фото1)
    await message.answer("Надішліть перше фото одягу:")


@router.message(AddShoes_Woman.фото1, F.photo)
async def add_photo1(message: Message, state: FSMContext):
    await state.update_data(фото1=message.photo[-1].file_id)
    await state.set_state(AddShoes_Woman.фото2)
    await message.answer("Надішліть друге фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Woman.фото2, F.photo)
async def add_photo2(message: Message, state: FSMContext):
    await state.update_data(фото2=message.photo[-1].file_id)
    await state.set_state(AddShoes_Woman.фото3)
    await message.answer("Надішліть третє фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Woman.фото3, F.photo)
async def add_photo3(message: Message, state: FSMContext):
    await state.update_data(фото3=message.photo[-1].file_id)
    await state.set_state(AddShoes_Woman.фото4)
    await message.answer("Надішліть четверте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Woman.фото4, F.photo)
async def add_photo4(message: Message, state: FSMContext):
    await state.update_data(фото4=message.photo[-1].file_id)
    await state.set_state(AddShoes_Woman.фото5)
    await message.answer("Надішліть п'яте фото (або натисніть 'Пропустити' для завершення):",reply_markup=kb.skip_photo_kb)


@router.message(AddShoes_Woman.фото5, F.photo)
async def add_photo5(message: Message, state: FSMContext):
    await state.update_data(фото5=message.photo[-1].file_id)
    await state.set_state(AddShoes_Woman.tg_link)
    await message.answer("Введіть tg_link продавця:",reply_markup=ReplyKeyboardRemove())


@router.message(AddShoes_Woman.tg_link)
async def add_tg_link(message: Message, state: FSMContext):
    await state.update_data(tg_link=message.text)
    await save_cloth_to_db(state, WomanShoes)
    await state.clear()
    await message.answer("Жіноче взуття успішно додано до бази даних.", reply_markup=kb.menu)