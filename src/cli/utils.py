from src.database import UrlRecheckRequest
from src.bot_messages import BotMessages
from src.bot import tele_bot
from aiogram.exceptions import TelegramForbiddenError
from rich import print as r_print
BANNER ="""
    _          _   _   ____  _     _     _               
   / \   _ __ | |_(_) |  _ \| |__ (_)___| |__   ___ _ __ 
  / _ \ | '_ \| __| | | |_) | '_ \| / __| '_ \ / _ \ '__|
 / ___ \| | | | |_| | |  __/| | | | \__ \ | | |  __/ |   
/_/   \_\_| |_|\__|_| |_|   |_| |_|_|___/_| |_|\___|_|"""
CRIDETIALS = """\u001b[34m
Developed By: wwaramii
From: https://t.me/wwow_bots
Project Github: https://github.com/wwarami/anti-phisher-bot
"""
FLAG = """
\u001b[31m|||||||||||||||||||||||
\u001b[37m|||||||||| \u001b[33m|| \u001b[37m|||||||||
\u001b[32m|||||||||||||||||||||||"""

def print_banner():
    print(BANNER)
    print(FLAG)
    print(CRIDETIALS)


async def send_recheck_request_response_to_user(recheck_request: UrlRecheckRequest):
    try:
        request_date_str = recheck_request.request_date.strftime("%m/%d/%Y, %H:%M:%S")
        checked_date_str = recheck_request.checked_date.strftime("%m/%d/%Y, %H:%M:%S") if recheck_request.checked_date else '<code>هنوز بررسی نشده است.</code>'
        response = BotMessages().recheck_request_report.format(
                id=recheck_request.id,
                url_id=recheck_request.url_id,
                url_string=recheck_request.url.url_string,
                first_result='✅' if recheck_request.url.is_valid else '❌',
                is_checked= '✅' if recheck_request.is_checked else '❌',
                new_is_valid= '✅' if recheck_request.new_is_valid else '❌',
                request_date=request_date_str,
                checked_date=checked_date_str)
        
        await tele_bot.send_message(chat_id=recheck_request.from_user_id,
                                    text=BotMessages().recheck_request_response.format(recheck_response=response))
    except TelegramForbiddenError:
        r_print('[red bold]Could not send user the update as the bot is blocked![/red bold]')
    except Exception as ex:
        r_print(f'[red bold]Could not send user the update as this exception was raised!: Type:{type(ex)}, message: {ex}[/red bold]')
