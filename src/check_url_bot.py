from src.database import AsyncDatabaseManager
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from src.bot_messages import BotMessages
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    CallbackQuery   
)
from src.utils import check_for_https_url, check_for_psp

main_router = Router()

class UrlCheckRequestState(StatesGroup):
    url = State()
    recheck_request = State()

CHANNELS = [
    "@sevlighter",
    "@whybots"
]


@main_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BotMessages().start, reply_markup=generate_defualt_keyboard())


@main_router.message(F.text == "🔗 بررسی آدرس")
async def handle_check_url(message: Message, state: FSMContext):
    is_verified = await verify_user(message)
    if not is_verified: return

    await state.set_state(UrlCheckRequestState.url)
    await message.answer(BotMessages().check_url, reply_markup=generate_cancel_keyboard())


@main_router.message(UrlCheckRequestState.url)
async def check_url_state(message: Message, state: FSMContext):
    is_verified = await verify_user(message)
    if not is_verified: return

    if message.text is None:
        await message.reply('❌ لطفا یک آدرس معتبر وارد کنید.')
        return
    
    url = message.text.strip().lower()
    is_https = check_for_https_url(url)
    is_valid_psp = check_for_psp(url)

    url_db = await AsyncDatabaseManager().create_url(url_string=url)
    await state.update_data(url=url_db.id)
    await state.set_state(UrlCheckRequestState.recheck_request)


    await message.answer(
        BotMessages().url_checked.format(no_ssl=BotMessages().unsafe_ssl if not is_https else '',
                                        has_ssl=BotMessages().safe_ssl if is_https else '',
                                        not_safe_psp=BotMessages().not_psp if not is_valid_psp else '',
                                        is_safe_psp=BotMessages().is_psp.format(psp_name=is_valid_psp[1], psp_address=is_valid_psp[0]) if is_valid_psp else '',
                                        url_code=url_db.id),
                                        reply_markup=generate_recheck_request_keyboad()
    )


@main_router.message(UrlCheckRequestState.recheck_request and F.text == "🔁 درخواست بررسی دوباره آدرس")
async def handle_recheck_request(message: Message, state: FSMContext):
    is_verified = await verify_user(message)
    if not is_verified: return
    state_data = await state.get_data()
    url_id = state_data.get("url")
    await state.clear()
    if url_id:
        await AsyncDatabaseManager().create_recheck_request(from_user_id=message.from_user.id, url_id=url_id)
        await message.answer(BotMessages().success_recheck_request, reply_markup=generate_defualt_keyboard())
    else:
        await message.answer(BotMessages().failed_recheck_request, reply_markup=generate_defualt_keyboard())
    

@main_router.message(F.text == '🔙 بازگشت')
async def handle_cancel_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('<b> ✨ عملیات جاری کنسل شد. </b>', reply_markup=generate_defualt_keyboard())


@main_router.callback_query(F.data == "check_am_i_joined")
async def check_user_is_joined(callback_query: CallbackQuery):
    is_member = await check_joined_channels(bot=callback_query.bot, user_id=callback_query.from_user.id)
    if is_member:
        await callback_query.answer("✅ شما جوین چنل های ما شدین. میتونین از ربات استفاده کنین.")
        await callback_query.message.delete()
    else:
        await callback_query.answer("❌ شما هنوز جوین چنل ها نشدین.")


async def verify_user(message: Message) -> bool:
    is_memeber = await check_joined_channels(bot=message.bot, user_id=message.from_user.id)
    if not is_memeber:
        await message.answer(text=BotMessages().join_channels, reply_markup=generate_join_channels_keyboard())
        return False
    return True


async def check_joined_channels(bot: Bot, user_id: str, channel_ids=CHANNELS):
    try:
        for channel_id in channel_ids:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status.value in ["creator", "administrator", "member"]:pass
            else: return False
    except Exception as ex:
        raise ex
    else:
        return True


def generate_join_channels_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for channel_id in CHANNELS:
        buttons.append(
            [InlineKeyboardButton(text=f'📌 {channel_id}', url=f't.me/{channel_id[1:]}')]
        )
    buttons.append([InlineKeyboardButton(text="✅ جوین شدم", callback_data="check_am_i_joined")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_defualt_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔗 بررسی آدرس")],
        [KeyboardButton(text="🔁 درخواست های بررسی من"), KeyboardButton(text="📋 درمورد آنتی فیشر")],
    ], 
    resize_keyboard=True
    )

def generate_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🔙 بازگشت')]
    ],
    resize_keyboard=True
    )

def generate_recheck_request_keyboad() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔁 درخواست بررسی دوباره آدرس")],
        [KeyboardButton(text='🔙 بازگشت')]
    ], resize_keyboard=True)
