from telegram.ext import Updater
from config import TOKEN
import threading
from telegram.ext import CommandHandler, Filters, MessageHandler
from check import sys_recheck
from func import start, help_info, tg_bind, tg_check, tg_update, tg_get_link, new_member, renew_link


thread = threading.Thread(target=sys_recheck)
thread.start()


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


start_handler = CommandHandler('start', start)
help_info_handler = CommandHandler('help', help_info)
bind_handler = CommandHandler('bind', tg_bind)
check_handler = CommandHandler('check', tg_check)
update_handler = CommandHandler('update', tg_update)
get_link_handler = CommandHandler('link', tg_get_link)
renew_link_handler = CommandHandler('relink', renew_link)
get_new_member = MessageHandler(Filters.status_update.new_chat_members, new_member)


dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_info_handler)
dispatcher.add_handler(bind_handler)
dispatcher.add_handler(check_handler)
dispatcher.add_handler(update_handler)
dispatcher.add_handler(get_link_handler)
dispatcher.add_handler(renew_link_handler)
dispatcher.add_handler(get_new_member)


updater.start_polling()
