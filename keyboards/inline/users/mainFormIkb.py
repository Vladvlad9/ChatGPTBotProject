import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData

from config import CONFIG
from crud import CRUDUser, CRUDSubscription
from crud.referralCRUD import CRUDReferral
from handlers.users.base_text import BaseText
from loader import bot
from schemas import UserSchema, ReferralSchema

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForms:
    @staticmethod
    async def check_sub_channel(user_id: int):
        try:
            chat_member = await bot.get_chat_member(chat_id=str(CONFIG.CHANNEL.CHANNEL_ID), user_id=user_id)
            if chat_member['status'] == 'left':
                return False
            return True
        except Exception as e:
            logging.error(f'Error check sub channel: {e}')

    @staticmethod
    async def main_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="👤Мой профиль",
                                         callback_data=main_cb.new("myProfile", "getProfile", 0, 0)),
                ],
                [
                    InlineKeyboardButton(text="💬Новый диалог",
                                         callback_data=main_cb.new("newDialogue", "getDialog", 0, 0)),
                    InlineKeyboardButton(text="🆘Мне нужна помощь", callback_data=main_cb.new("help", "getHelp", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def getDialog_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✔️Подписка",
                                         callback_data=main_cb.new("newDialogue", "SubscriptionGPT", 0, 0)),
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def my_profile_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💵 Купить подписку ChatGPT",
                                         callback_data=main_cb.new("myProfile", "subscriptionGPT", 0, 0)),
                ],
                [
                    InlineKeyboardButton(text="🤝 Получить 3 запроса ChatGPT",
                                         callback_data=main_cb.new("myProfile", "get_inquiries", 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def pay_subscription_ikb(targetMain: str,
                                   actionMain: str, targetBack: str, actionBack: str) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=f"{name.name} за {name.price},00 ₽",
                                                         callback_data=main_cb.new(targetMain,
                                                                                   actionMain, name.id, 0))
                                ]
                                for name in await CRUDSubscription.get_all()
                            ] + [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=main_cb.new(targetBack, actionBack, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def help_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛠️ Техническая поддержка",
                                         url=CONFIG.HELP.TechnicalSupport),
                ],
                [
                    InlineKeyboardButton(text="❔ Реклама и прочие вопросы",
                                         url=CONFIG.HELP.AdvertisingOtherIssues),
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Main", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def sub_channel_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Перейти в канал", url=CONFIG.CHANNEL.CHANNEL_NAME),
                    InlineKeyboardButton(text="Я подписался", callback_data=main_cb.new("subChannelDone", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def back_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)

                if data.get("target") == "Main":
                    text = await BaseText.base_txt_main_form()
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForms.main_ikb())

                elif data.get("target") == "subChannelDone":
                    text = await BaseText.base_txt_main_form()

                    if await MainForms.check_sub_channel(user_id=callback.from_user.id):
                        get_user = await CRUDUser.get(user_id=callback.from_user.id)
                        if not get_user:
                            await CRUDUser.add(user=UserSchema(user_id=callback.from_user.id))

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.main_ikb())
                    else:
                        try:
                            await callback.message.edit_text(text="Вы не подписались на канал!!",
                                                             reply_markup=await MainForms.sub_channel_ikb())
                        except Exception as e:
                            await callback.message.edit_text(text="Вы все еще не подписались на канал!",
                                                             reply_markup=await MainForms.sub_channel_ikb())

                elif data.get('target') == "myProfile":
                    if data.get('action') == "getProfile":
                        text = "💬 Доступно запросов для ChatGPT: 3\n\n" \
                               "Зачем запросы ChatGPT?\n\n" \
                               "Задавая вопросы - ты тратишь 1 запрос. " \
                               "Бесплатно можно тратить 3 запроса каждый день. " \
                               "Запросы восстанавливаются каждый день в 06:00\n\n" \
                               "Не хватает запросов ChatGPT?\n\n" \
                               "- Вы можете купить подписку для ChatGPT и не париться о лимитах.\n" \
                               "- Пригласи человека и получи за него 3 запроса ChatGPT " \
                               "и 1 запрос на генерацию изображения.\n\n" \
                               "Как правильно общаться с ChatGPT " \
                               '<a href="https://telegra.ph/Gajd-Kak-sostavit-horoshij-zapros-v-ChatGPT-s-primerami' \
                               '-04-08-2">Узнать</a>'

                        await callback.message.edit_text(text=text,
                                                         parse_mode="HTML",
                                                         disable_web_page_preview=True,
                                                         reply_markup=await MainForms.my_profile_ikb())

                    elif data.get('action') == "subscriptionGPT":
                        text = "Выберите тарифный план, который хотите приобрести."
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.pay_subscription_ikb(
                                                             targetMain="myProfile",
                                                             actionMain="subscriptionGPT",
                                                             targetBack="myProfile",
                                                             actionBack="getProfile"
                                                         ))

                    elif data.get('action') == "get_inquiries":
                        get_referral = await CRUDReferral.get_all(user_id=callback.from_user.id)
                        text = "🤝 Зарабатывайте запросы с нашей реферальной системой\n\n" \
                               "С каждого приглашенного пользователя вы получаете: 3 запроса ChatGPT\n\n" \
                               f"Приглашено за все время вами человек: <i>{len(get_referral)}</i>\n\n" \
                               f"Ваша пригласительная ссылка: " \
                               f"<code>https://t.me/all_bot_test_bot?start={callback.from_user.id}</code>"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb(target="myProfile",
                                                                                               action="getProfile"),
                                                         disable_web_page_preview=False,
                                                         parse_mode="HTML")

                elif data.get('target') == "newDialogue":
                    if data.get('action') == "getDialog":
                        get_user = await CRUDUser.get(user_id=callback.from_user.id)
                        if get_user:
                            text = "🤖 Привет! Я ChatGPT. Чем я могу тебе помочь?\n" \
                                   f"У тебя осталось {get_user.queries_chat_gpt} запросов"

                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.getDialog_ikb())

                    elif data.get('action') == "SubscriptionGPT":
                        try:
                            text = "Выберите тарифный план, который хотите приобрести1."
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.pay_subscription_ikb(
                                                                 targetMain="newDialogue",
                                                                 actionMain="SubscriptionGPT",
                                                                 targetBack="newDialogue",
                                                                 actionBack="getDialog"
                                                             ))
                        except Exception as e:
                            pass

                elif data.get('target') == "help":
                    if data.get('action') == "getHelp":
                        text = "🛠️ При обращении в техническую поддержку, ... "

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.help_ikb())

