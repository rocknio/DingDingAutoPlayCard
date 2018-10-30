# -*- coding: utf-8 -*-
import subprocess
import time
from tornado import ioloop
import datetime
import random
import configparser

config = configparser.ConfigParser(allow_no_value=False)
config.read("dingding.cfg")
go_hour = int(config.get("time", "go_hour"))
back_hour = int(config.get("time", "back_hour"))
directory = config.get("ADB", "directory")
is_debug = int(config.get("GLOBAL", "is_debug"))


# 打开钉钉，关闭钉钉封装为一个妆饰器函数
def with_open_close_dingding(func):
    def wrapper(self, *args, **kwargs):
        print("打开钉钉")
        operation_list = [self.adbpower, self.adbclear, self.adbopen_dingding]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        # 确保完全启动，并且加载上相应按键
        time.sleep(15)
        print("打开钉钉成功")
        print("打开企业考勤界面")
        operation_list1 = [self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        time.sleep(15)
        print("打开企业考勤界面成功")

        # 包装函数
        func(self, *args, **kwargs)

        print("关闭钉钉")
        operation_list2 = [self.adbback_index, self.adbkill_dingding, self.adbpower]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("关闭钉钉成功")

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
        # self.adbpull = '"%s\\adb" pull sdcard/screen.png %s' % (adb_dir, screen_dir)
        # 删除设备截屏
        self.adbrm_screencap = '"%s\\adb" shell rm -r sdcard/screen.png' % adb_dir

    # 上班(极速打卡)
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
        print("上班打卡成功")

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
        print("下班打卡成功")


def get_tomorrow_call_time(hour, minute):
    tomorrow = int(time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d')))
    return tomorrow + (hour * 3600) + (minute * 60)


def get_today_call_time(hour, minute):
    today = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
    return today + (hour * 3600) + (minute * 60)


def call_later_delay(func, hour, minute):
    return func(hour, minute) - int(datetime.datetime.now().timestamp())


def do_goto_work():
    DingDing(directory).goto_work()
    setup_after_work()


def do_after_work():
    DingDing(directory).after_work()
    ioloop.IOLoop.instance().call_later(60 * 60, start_loop)


def setup_after_work():
    random_time = random.randint(5, 30)
    delay = abs(call_later_delay(get_today_call_time, back_hour, random_time))
    ioloop.IOLoop.instance().call_later(delay, do_after_work)


def setup_goto_work():
    random_time = random.randint(30, 59)
    delay = abs(call_later_delay(get_today_call_time, go_hour, random_time))
    ioloop.IOLoop.instance().call_later(delay, do_goto_work)


# 任务调度
def start_loop():
    """
    判断上下班类型,确定上下班打卡时间
    :return: None
    """
    if is_weekend():
        ioloop.IOLoop.instance().call_later(60, start_loop)

    now_time = datetime.datetime.now()
    now_hour = now_time.hour

    # 上班,小时对应，随机分钟对应
    if now_hour == go_hour:
        setup_goto_work()
    if now_hour == back_hour:
        setup_after_work()
    else:
        ioloop.IOLoop.instance().call_later(60, start_loop)


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


if __name__ == "__main__":
    try:
        ioloop.IOLoop.instance().call_later(1, start_loop)
        ioloop.IOLoop.instance().start()
    except Exception as err:
        print("err = {}".format(err))
