import sqlite3
import time
import requests
from telegram.ext import Updater
from config import TOKEN, ADMIN_ID, GROUP_ID, API_URL, BOT_USERNAME, CYCLE_TIME, IGNORE_LIST

updater = Updater(token=TOKEN, use_context=True)
bot = updater.bot


def get_invite_link():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("select * from link where id='newest'")
    url = cursor.fetchone()[1]
    conn.close()
    return url


def update_invite_link(invite_url):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("update link set url = ? where id='newest'", (invite_url, ))
    conn.commit()
    conn.close()


def check(id, email, firstname):
    try:
        # print(email)
        # print(firstname)
        api_return = requests.get('{}?email={}&firstname={}'.format(API_URL, email, firstname))
        api_rst = api_return.content.decode("utf-8")
        # print(api_rst)
        if api_rst == '认证成功！':
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user VALUES (?,?,?,?)", (id, email, firstname, 1))
            conn.commit()
            conn.close()
            return 1
        elif api_rst == '该用户没有注册！':
            return 2
        elif api_rst == '邮箱和用户名不匹配！':
            return 3
        elif api_rst == '该用户没有活跃的产品！':
            return 4
    except Exception as e:
        print(e)
        return 5


def bind(id, email, firstname):
    try:
        print("进入bind函数")
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("select * from user where id=?", (id,))
        print("准备打印数据库fetch")
        fetch = cursor.fetchone()
        print(fetch)
        print("打印数据库fetch，随后关闭连接")
        conn.close()
        if fetch is None:
            print('用户第一次绑定，进入验证流程！')
            result = check(id, email, firstname)
            if result == 1:
                return "绑定成功！"
            elif result == 2:
                return '该用户没有注册！'
            elif result == 3:
                return '邮箱和用户名不匹配！'
            elif result == 4:
                return '该用户没有活跃的产品！'
        else:
            print('用户已存在')
            if fetch[3] == 1:
                # print('您已经绑定，请勿重复操作！当前状态：已激活！')
                return '您已经绑定，请勿重复操作！当前状态：已激活！'
            else:
                # print('您已经绑定，请勿重复操作！当前状态：未激活！如需刷新状态，请发送 /check 指令')
                return '您已经绑定，请勿重复操作！当前状态：未激活！如需刷新状态，请发送 /check 指令'
    except Exception as e:
        print('bind 函数发生错误，返回随机错误')
        return '邮箱和用户名不匹配！'


def sys_recheck():
    while True:
        try:
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute("select * from user")
            user_list = cursor.fetchall()
            conn.close()
            for user in user_list:
                id = user[0]
                if int(id) not in IGNORE_LIST:
                    email = user[1]
                    firstname = user[2]
                    api_return = requests.get('{}?email={}&firstname={}'.format(API_URL, email, firstname))
                    api_rst = api_return.content.decode("utf-8")
                    conn = sqlite3.connect('db.sqlite3')
                    cursor = conn.cursor()
                    if api_rst == '认证成功！':
                        print('{} | 已更新用户状态，用户id：{}'.format(email, id))
                        cursor.execute("update user set active = 1 where id = ?", (id,))
                        # bot.unban_chat_member(-1001490625404, id, timeout=None, until_date=None)
                    elif api_rst == '该用户没有活跃的产品！':
                        print('{} | 该用户没有活跃的产品，用户id：{}'.format(email, id))
                        cursor.execute("update user set active = 0 where id = ?", (id,))
                        try:
                            print('尝试踢出{}|{}'.format(id, email))
                            bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
                        except Exception as e:
                            print(e)
                    elif api_rst == '该用户没有注册！':
                        print('{} | 该用户没有注册，用户id：{}'.format(email, id))
                        cursor.execute("update user set active = 0 where id = ?", (id,))
                        try:
                            print('尝试踢出{}|{}'.format(id, email))
                            bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
                        except Exception as e:
                            print(e)
                    elif api_rst == '邮箱和用户名不匹配！':
                        print('{} | 邮箱和用户名不匹配，用户id：{}'.format(email, id))
                        cursor.execute("update user set active = 0 where id = ?", (id,))
                        try:
                            print('尝试踢出{}|{}'.format(id, email))
                            bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
                        except Exception as e:
                            print(e)
                    conn.commit()
                    conn.close()
                    time.sleep(3)
    #         new_invite_link = bot.export_chat_invite_link(GROUP_ID, timeout=None)
    #         update_invite_link(new_invite_link)
            print('循环检测完毕，开始休眠{}s'.format(CYCLE_TIME))
            time.sleep(CYCLE_TIME)
        except Exception as e:
            print(e)
            print('sys_recheck 循环检测函数错误')


def user_check(id):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("select * from user where id=?", (id,))
        user_info = cursor.fetchone()
        conn.close()
        print('user_check 函数' + str(user_info))
        if user_info is None:
            return '您还未绑定，请使用 /bind 命令进行绑定操作！'
        else:
            email = user_info[1]
            firstname = user_info[2]
            active = user_info[3]
            print(email, firstname, active)
            api_return = requests.get('{}?email={}&firstname={}'.format(API_URL, email, firstname))
            api_rst = api_return.content.decode("utf-8")
            print(api_rst)
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            if api_rst == '认证成功！' and active == 0:
                cursor.execute("update user set active = 1 where id = ?", (id,))
                if id not in IGNORE_LIST:
                    bot.unban_chat_member(GROUP_ID, id, timeout=None, until_date=None)
            elif api_rst == '该用户没有活跃的产品！':
                cursor.execute("update user set active = 0 where id = ?", (id,))
                print('尝试踢出{}|{}'.format(id, email))
                bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
            elif api_rst == '该用户没有注册！':
                cursor.execute("update user set active = 0 where id = ?", (id,))
                print('尝试踢出{}|{}'.format(id, email))
                bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
            elif api_rst == '邮箱和用户名不匹配！':
                cursor.execute("update user set active = 0 where id = ?", (id,))
                print('尝试踢出{}|{}'.format(id, email))
                bot.kick_chat_member(GROUP_ID, id, timeout=None, until_date=None)
            print("状态已更新")
            conn.commit()
            conn.close()
            result = user_get_status(id)
            if result == 1:
                return '当前状态：已激活'
            else:
                return '当前状态：未激活'
    except Exception as e:
        print(e)
        print('user_check 函数错误')
        return '机器人暂时不可用，请稍后重试！'


def user_get_status(id):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("select * from user where id=?", (id,))
        user_info = cursor.fetchone()
        status = user_info[3]
        conn.close()
        if status == 1:
            print('user_get_status | 当前状态：已激活')
            return 1
        else:
            print('user_get_status | 当前状态：未激活')
            return 0
    except Exception as e:
        print(e)
        print('user_get_status 函数错误')
        return 1


def user_update(id, email, firstname):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("select * from user where id=?", (id,))
        fetch = cursor.fetchone()
        conn.close()
        print(fetch)
        if fetch is None:
            print('没有该用户绑定信息，进入绑定流程')
            result = bind(id, email, firstname)
            if result == "绑定成功！":
                return '数据库中没有您的信息，已经为您绑定激活！'
            elif result == '该用户没有注册！':
                return '数据库中没有您的信息，本次尝试为您直接绑定失败：邮箱未注册'
            elif result == '邮箱和用户名不匹配！':
                return '数据库中没有您的信息，本次尝试为您直接绑定失败：用户名不匹配'
            elif result == '该用户没有活跃的产品！':
                return '数据库中没有您的信息，本次尝试为您直接绑定失败：您没有激活中的产品'
        else:
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute("update user set email=?, firstname=?, active=0 where id=?", (email, firstname, id,))
            conn.commit()
            conn.close()
            status = user_check(id)
            return '更新成功！{}'.format(status)
    except Exception as e:
        print(e)
        print('user_update 函数发生错误，返回随机值')
        return '数据库中没有您的信息，本次尝试为您直接绑定失败：用户名不匹配'
# user_update(333, 'huyujievip@gmail.com', 'Allen Jones')


def new_member_check(id):
    try:
        print('新用户id:' + str(id))
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("select * from user where id=?", (id,))
        fetch = cursor.fetchone()
        print(fetch)
        conn.close()
        if fetch is None:
            try:
                if id not in IGNORE_LIST:
                    bot.unban_chat_member(GROUP_ID, id, timeout=None, until_date=None)
                    new_invite_link = bot.export_chat_invite_link(GROUP_ID, timeout=None)
                    print(new_invite_link)
                    update_invite_link(new_invite_link)
            except Exception as e:
                print(e)
            return False
        else:
            return True
    except Exception as e:
        print(e)
        print('新用户函数 new_member_check 错误')
        return True
