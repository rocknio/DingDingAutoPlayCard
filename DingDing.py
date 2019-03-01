# -*- coding: utf-8 -*-
import logging
import logging.handlers
import subprocess
import sys
import time
from tornado import ioloop
import random
import configparser
import datetime
# from twilio_sms.twilio_sms_utils import send_sms
from email_utils.email_utils import send_email

__author__ = 'Neo'

config = configparser.ConfigParser(allow_no_value=False)
config.read("dingding.cfg")
go_hour = int(config.get("time", "go_hour"))
back_hour = int(config.get("time", "back_hour"))
directory = config.get("ADB", "directory")
is_debug = int(config.get("GLOBAL", "is_debug"))
dest_email = config.get("email", 'dest_email')


def init_logging():
    """
    日志文件设置
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    # file_log = logging.handlers.TimedRotatingFileHandler('dingding.log', 'MIDNIGHT', 1, 0)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-7s] [%(module)s:%(filename)s-%(funcName)s-%(lineno)d] %(message)s')
    sh.setFormatter(formatter)
    # file_log.setFormatter(formatter)

    logger.addHandler(sh)
    # logger.addHandler(file_log)

    logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))


# 打开钉钉，关闭钉钉封装为一个妆饰器函数
def with_open_close_dingding(func):
    def wrapper(self, *args, **kwargs):
        logging.info("打开钉钉")
        operation_list = [self.adbpower, self.adbclear, self.adbopen_dingding]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        # 确保完全启动，并且加载上相应按键
        time.sleep(25)
        logging.info("打开钉钉成功")
        logging.info("打开企业考勤界面")
        operation_list1 = [self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        time.sleep(25)
        logging.info("打开企业考勤界面成功")

        # 包装函数
        func(self, *args, **kwargs)

        logging.info("关闭钉钉")
        operation_list2 = [self.adbback_index, self.adbkill_dingding, self.adbpower]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        logging.info("关闭钉钉成功")

    return wrapper


class DingDing:
    # 初始化，设置adb目录
    def __init__(self, adb_dir):
        self.directory = adb_dir
        # 点亮屏幕
        self.adbpower = '"%s\\adb" shell input keyevent 26' % adb_dir
        # 滑屏解锁
        self.adbclear = '"%s\\adb" shell input swipe %s' % (adb_dir, config.get("position", "light_position"))
        # 启动钉钉应用
        self.adbopen_dingding = '"%s\\adb" shell monkey -p com.alibaba.android.rimet -c android.intent.category.LAUNCHER 1' % adb_dir
        # 关闭钉钉
        self.adbkill_dingding = '"%s\\adb" shell am force-stop com.alibaba.android.rimet' % adb_dir
        # 返回桌面
        self.adbback_index = '"%s\\adb" shell input keyevent 3' % adb_dir
        # 点击工作
        self.adbselect_work = '"%s\\adb" shell input tap %s' % (adb_dir, config.get("position", "work_position"))
        # 点击考勤打卡
        self.adbselect_playcard = '"%s\\adb" shell input tap %s' % (adb_dir, config.get("position", "check_position"))
        # 点击上班打卡
        self.adbclick_goto_work_playcard = '"%s\\adb" shell input tap %s' % (adb_dir, config.get("position", "go_to_work_position"))
        # 点击下班打卡
        self.adbclick_after_work_playcard = '"%s\\adb" shell input tap %s' % (adb_dir, config.get("position", "after_position"))
        # 设备截屏保存到sdcard
        self.adbscreencap = '"%s\\adb" shell screencap -p sdcard/screen.png' % adb_dir
        # 传送到计算机
        self.adbpull = '"%s\\adb" pull sdcard/screen.png %s' % (adb_dir, ".\\screen_cap")
        # 删除设备截屏
        self.adbrm_screencap = '"%s\\adb" shell rm -r sdcard/screen.png' % adb_dir

    # 上班
    @with_open_close_dingding
    def goto_work(self):
        if is_debug != 1:
            operation_list = [self.adbclick_goto_work_playcard]
            for operation in operation_list:
                process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
                process.wait()
                time.sleep(3)
        else:
            print(self.adbclick_goto_work_playcard)
        logging.info("上班打卡成功")

    # 极速打卡上下班
    @with_open_close_dingding
    def work_rapidly(self):
        if is_debug != 1:
            operation_list = [self.adbscreencap, self.adbpull, self.adbrm_screencap]
            for operation in operation_list:
                process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
                process.wait()
                time.sleep(3)
        else:
            print(self.adbclick_goto_work_playcard)
        logging.info("上班打卡成功")

    # 下班
    @with_open_close_dingding
    def after_work(self):
        if is_debug != 1:
            operation_list = [self.adbclick_after_work_playcard]
            for operation in operation_list:
                process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
                process.wait()
                time.sleep(3)
        else:
            print(self.adbclick_after_work_playcard)
        logging.info("下班打卡成功")


def get_tomorrow_call_time(hour, minute):
    tomorrow = int(time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d')))
    return tomorrow + (hour * 3600) + (minute * 60)


def get_today_call_time(hour, minute):
    today = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
    return today + (hour * 3600) + (minute * 60)


def call_later_delay(func, hour, minute):
    return func(hour, minute) - int(datetime.datetime.now().timestamp())


def do_goto_work():
    DingDing(directory).work_rapidly()
    send_email(dest_email, "上班打卡时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    set_next_loop(60 * 60, start_loop)


def do_after_work():
    DingDing(directory).work_rapidly()
    send_email(dest_email, "下班打卡时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    set_next_loop(60 * 60, start_loop)


def setup_after_work():
    random_time = random.randint(0, 10)
    delay = abs(call_later_delay(get_today_call_time, back_hour, random_time))
    logging.info(">>> 将在{}打卡下班".format((datetime.datetime.now() + datetime.timedelta(seconds=delay)).strftime('%Y-%m-%d %H:%M:%S')))
    time.sleep(delay)
    do_after_work()


def setup_goto_work():
    random_time = random.randint(0, 10)
    delay = abs(call_later_delay(get_today_call_time, go_hour, random_time))
    logging.info("<<< 将在{}打卡上班".format((datetime.datetime.now() + datetime.timedelta(seconds=delay)).strftime('%Y-%m-%d %H:%M:%S')))
    time.sleep(delay)
    do_goto_work()


def set_next_loop(delay_seconds, func):
    logging.info("Call {} at {} seconds later: {}".format(func, delay_seconds, (datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)).strftime('%Y-%m-%d %H:%M:%S')))
    ioloop.IOLoop.instance().call_later(delay_seconds, func)


# 任务调度
def start_loop():
    """
    判断上下班类型,确定上下班打卡时间
    :return: None
    """
    if is_weekend():
        set_next_loop(60, start_loop)
        return

    now_time = datetime.datetime.now()
    now_hour = now_time.hour

    # 上班,小时对应，随机分钟对应
    if now_hour == go_hour:
        setup_goto_work()
    elif now_hour == back_hour:
        setup_after_work()
    else:
        set_next_loop(60, start_loop)


# 是否是周末
def is_weekend():
    """
    :return: if weekend return True else return False
    """
    now_time = datetime.datetime.now().strftime("%w")
    if now_time == "6" or now_time == "0":
        return True
    else:
        return False


def check_python_version():
    if sys.version[:1] != '3':
        return False
    else:
        return True


if __name__ == "__main__":
    try:
        if check_python_version() is False:
            print('Please use python3 to run the program')
            exit()

        init_logging()

        ioloop.IOLoop.instance().call_later(1, start_loop)
        ioloop.IOLoop.instance().start()
    except Exception as err:
        print("err = {}".format(err))
