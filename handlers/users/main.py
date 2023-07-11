from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud.referralCRUD import CRUDReferral
from crud.userCRUD import CRUDUser
from handlers.users.base_text import BaseText
from keyboards.inline.users.mainFormIkb import main_cb, MainForms
from loader import dp, bot
import logging

from schemas import UserSchema, ReferralSchema
from states.users.userStates import UserStates


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    text = await BaseText.base_txt_main_form()

    if message.get_args():
        await CRUDReferral.add(referral=ReferralSchema(user_id=int(message.get_args()),
                                                       referral_id=message.from_user.id))
        current_user = await CRUDUser.get(user_id=int(message.get_args()))
        current_user.queries_chat_gpt += 3
        await CRUDUser.update(user_id=current_user)

    if await MainForms.check_sub_channel(user_id=message.from_user.id):
        get_user = await CRUDUser.get(user_id=message.from_user.id)

        if not get_user:
            await CRUDUser.add(user=UserSchema(user_id=message.from_user.id))

        await message.answer(text=text,
                             reply_markup=await MainForms.main_ikb())
    else:
        await message.answer(text="Вы не подписались на канал!",
                             reply_markup=await MainForms.sub_channel_ikb())


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)
