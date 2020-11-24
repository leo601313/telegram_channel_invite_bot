from check import bind, user_check, user_update, new_member_check
from telegram.ext import Updater
from config import TOKEN, ADMIN_ID, GROUP_ID, API_URL, BOT_USERNAME
import sqlite3
from check import update_invite_link, get_invite_link

updater = Updater(token=TOKEN, use_context=True)
bot = updater.bot


def tg_echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="这是我刚才收到的信息: " + "*" + update.message.text + "*",
                             parse_mode='Markdown')


def get_user_input(update, context):
    user = update.message.from_user
    id = user.id
    email = context.args[0]
    firstname = ''
    print(context.args[0], context.args[1], context.args[2])
    try:
        for i in context.args[1:]:
            firstname = firstname + ' ' + i
    except:
        print('变量缺失')
    firstname = firstname[1:]
    input_list = [id, email, firstname]
    return input_list


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! 发送 /help 获取命令信息", parse_mode='Markdown')


def help_info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="/bind *邮箱* *用户名* ｜ 绑定 \n"
                                  "/update *邮箱* *用户名* | 更新 \n"
                                  "/check | 获取当前状态\n"
                                  "/link | 激活状态下获取群组链接\n",
                             parse_mode='Markdown')


def is_legal(update, context):
    if update.effective_chat.type != 'private':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='该命令为*敏感操作*\n请私聊 {} ，以免泄露您的隐私'.format(BOT_USERNAME),
            parse_mode='Markdown'
        )
        return False
    else:
        return True


def is_empty(update, context):
    try:
        if ''.join(context.args) == '':
            print('缺少参数')
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='*参数错误*，请检查后重新输入 \n如需查看指令信息，请输入 /help 指令',
                parse_mode='Markdown'
            )
            return False
        else:
            return True
    except Exception as e:
        print(e)
        print('is_empty 函数错误，返回失败值')
        return False


def is_admin(update, context):
    try:
        if update.message.from_user.id in ADMIN_ID:
            return True
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='*非管理员，无权操作*',
                parse_mode='Markdown'
            )
            return False
    except Exception as e:
        print(e)
        print('is_admin 函数错误，返回失败值')
        return False


def tg_bind(update, context):
    # print(update.message)
    print("进入tg_bind函数")
    try:
        if is_legal(update, context) and is_empty(update, context):
            user = update.message.from_user
            id = user.id
            input_list = get_user_input(update, context)
            print(input_list[0], input_list[1], input_list[2])
            result = bind(input_list[0], input_list[1], input_list[2])
            if result == '绑定成功！':
                # invite_link = context.bot.export_chat_invite_link(GROUP_ID, timeout=None)
                invite_link = get_invite_link()
                print(invite_link)
                print("tg推送消息")
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="*" + result + "*" + '*群组链接*:\n{}'.format(invite_link),
                    parse_mode='Markdown'
                )
                print('send_message发送完毕')
            else:
                print("绑定失败")
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=result,
                    parse_mode='Markdown'
                )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='格式错误，请重试！',
            )
    except Exception as e:
        print(e)
        print('tg_bind 函数错误')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='机器人处于暂时不可用状态，请稍后重试',
            parse_mode='Markdown'
        )


def tg_get_link(update, context):
    try:
        if is_legal(update, context):
            user = update.message.from_user
            print("进入tg_get_link | 调用user_check")
            result = user_check(user.id)
            print('tg_get_link | ' + result)
            if result == '您还未绑定，请使用 /bind 命令进行绑定操作！':
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=result,
                    parse_mode='Markdown'
                )
            if result == '当前状态：未激活':
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="*" + result + "*" + '. 您无权进入群组\n请使用 /update 指令更新信息后重试！',
                    parse_mode='Markdown'
                )
            if result == '当前状态：已激活':
                # invite_link = context.bot.export_chat_invite_link(GROUP_ID, timeout=None)
                invite_link = get_invite_link()
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="*" + result + "*" + '. *群组链接*:\n{}'.format(invite_link),
                    parse_mode='Markdown'
                )
    except Exception as e:
        print(e)
        print('tg_get_link 函数错误')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='机器人处于暂时不可用状态，请稍后重试',
            parse_mode='Markdown'
        )


def tg_check(update, context):
    try:
        user = update.message.from_user
        result = user_check(user.id)
        if result == '当前状态：未激活':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="*" + result + "*" + ". 您无权进入群组\n请使用 /update 指令更新信息后重试！",
                parse_mode='Markdown'
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result,
                parse_mode='Markdown'
            )
    except Exception as e:
        print(e)
        print('tg_check 函数错误')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='机器人暂时不可用，请稍后重试！',
            parse_mode='Markdown'
        )


def tg_update(update, context):
    try:
        if is_legal(update, context) and is_empty(update, context):
            print('进入update函数')
            input_list = get_user_input(update, context)
            print("输出用户输入数据")
            print(input_list[0], input_list[1], input_list[2])
            result = user_update(input_list[0], input_list[1], input_list[2])
            print("输出更新函数返回result")
            print(result)
            if result == "更新成功！当前状态：已激活":
                print("用户已激活，返回invite链接")
                # invite_link = context.bot.export_chat_invite_link(GROUP_ID, timeout=None)
                invite_link = get_invite_link()
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="*" + result + "*" + '\n*群组链接*:\n{}'.format(invite_link),
                    parse_mode='Markdown'
                )
            else:
                print("用户未激活，返回result")
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=result,
                    parse_mode='Markdown'
                )
    except Exception as e:
        print(e)
        print('tg_update 函数错误')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='机器人暂时不可用，请稍后重试！',
            parse_mode='Markdown'
        )


def renew_link(update, context):
    try:
        # print('进入判断函数')
        if is_admin(update, context):
            print('该用户为admin，进入更新流程')
            new_invite_link = context.bot.export_chat_invite_link(GROUP_ID, timeout=None)
            print(new_invite_link)
            update_invite_link(new_invite_link)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="*" + "邀请链接已更新，已同步至数据库" + "*",
                parse_mode='Markdown'
            )
    except Exception as e:
        print(e)
        print('renew_link 函数错误')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='机器人暂时不可用，请稍后重试！',
            parse_mode='Markdown'
        )


def new_member(update, context):
    try:
        id = update.message.new_chat_members[0].id
        if not new_member_check(id):
            print(123)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="发现一名入侵者，已经移除，并已更新群组链接",
                parse_mode='Markdown'
            )
    except Exception as e:
        print(e)
        print('new_member 函数错误')


# def tg_ban(update, context):
#
#     print('进入ban函数')
#     chat = update.effective_chat
#     print(chat.type)
#     print(chat.id)
#     result = context.bot.kick_chat_member(chat.id, 375511601, timeout=None, until_date=None)
#     result = context.bot.unban_chat_member(-1001244136691, 375511601, timeout=None, until_date=None)
#     result = context.bot.export_chat_invite_link(-1001244136691, timeout=None)
#     promote_chat_member export_chat_invite_link
#     result = Bot.leave_chat(chat.id, timeout=None)
#     result = Bot.kick_chat_member(chat.id, 375511601, timeout=None, until_date=None, )
#     print(result)
#     print('运行结束')
