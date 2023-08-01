import time

import openai
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

from message_templates import message_templates
from schemas import UserSchema, ReferralSchema
from states.users.userStates import UserStates

messages = {}


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


@dp.message_handler(commands=['start'], state=UserStates.all_states)
async def new_topic_cmd(message: types.Message):
    try:
        userid = message.from_user.username
        messages[str(userid)] = []
        text = await BaseText.base_txt_main_form()
        await message.answer(text=text,
                             reply_markup=await MainForms.main_ikb())
    except Exception as e:
        logging.error(f'Error in new_topic_cmd: {e}')


@dp.message_handler(state=UserStates.Query)
async def echo_msg(message: types.Message, state: FSMContext = None):
    user = await CRUDUser.get(user_id=message.from_user.id)
    if user:
        if user.queries_chat_gpt == 0:
            await message.answer(text="У вас закончились запросы!",
                                 reply_markup=await MainForms.getDialog_ikb())
            await state.finish()
        else:
            user_languages = {}
            try:
                user_message = message.text
                userid = message.from_user.username
                if userid not in messages:
                    messages[userid] = []
                messages[userid].append({"role": "user", "content": user_message})
                messages[userid].append({"role": "user",
                                         "content": f"chat: {message.chat} Now {time.strftime('%d/%m/%Y %H:%M:%S')} user: "
                                                    f"{message.from_user.first_name} message: {message.text}"})
                logging.info(f'{userid}: {user_message}')

                should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

                if should_respond:
                    language = user_languages.get(message.from_user.id, 'ru')
                    processing_message = await message.reply(message_templates[language]['processing'])

                    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

                    completion = await openai.ChatCompletion.acreate(
                        model="gpt-3.5-turbo",
                        messages=messages[userid],
                        max_tokens=2500,
                        temperature=0.7,
                        frequency_penalty=0,
                        presence_penalty=0,
                        user=userid
                    )
                    chatgpt_response = completion.choices[0]['message']

                    messages[userid].append({"role": "assistant", "content": chatgpt_response['content']})
                    logging.info(f'ChatGPT response: {chatgpt_response["content"]}')

                    await message.reply(chatgpt_response['content'])
                    user.queries_chat_gpt -= 1
                    await CRUDUser.update(user=user)

                    await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

            except Exception as ex:
                if ex == "context_length_exceeded":
                    language = user_languages.get(message.from_user.id, 'en')
                    await message.reply(message_templates[language]['error'])
                    await new_topic_cmd(message)
                    await echo_msg(message)


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)
