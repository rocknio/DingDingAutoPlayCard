# -*- coding: utf-8 -*-
import subprocess
import time
import sched
import datetime
import random
import configparser

config = configparser.ConfigParser(allow_no_value=False)
config.read("dingding.cfg")
scheduler = sched.scheduler(time.time, time.sleep)
go_hour = int(config.get("time", "go_hour"))
back_hour = int(config.get("time", "back_hour"))
directory = config.get("ADB", "directory")
is_debug = config.get("GLOBAL", "is_debug")


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
        # 点击下班打卡
        self.adbclick_playcard = '"%s\\adb" shell input tap %s' % (adb_dir, config.get("position", "play_position"))
        # 设备截屏保存到sdcard
        self.adbscreencap = '"%s\\adb" shell screencap -p sdcard/screen.png' % adb_dir
        # 传送到计算机
        # self.adbpull = '"%s\\adb" pull sdcard/screen.png %s' % (adb_dir, screen_dir)
        # 删除设备截屏
        self.adbrm_screencap = '"%s\\adb" shell rm -r sdcard/screen.png' % adb_dir

    # 上班(极速打卡)
    @with_open_close_dingding
    def goto_work(self):
        if is_debug == 1:
            operation_list = [self.adbclick_playcard]
            for operation in operation_list:
                process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
                process.wait()
                time.sleep(3)
        else:
            print(self.adbclick_playcard)
        print("上班打卡成功")

    # 下班
    @with_open_close_dingding
    def after_work(self):
        if is_debug == 1:
            operation_list = [self.adbclick_playcard]
            for operation in operation_list:
                process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
                process.wait()
                time.sleep(3)
        else:
            print(self.adbclick_playcard)
        print("下班打卡成功")


# 随机打卡时间段
def random_minute():
    return random.randint(30, 50)


# 包装循环函数，传入随机打卡时间点
def incode_loop(func, minute):
    """
    包装start_loop任务调度函数，主要是为了传入随机分钟数。保证在不打卡的情况下能保持分钟数不变。
    :param func: star_loop
    :param minute: 随机分钟数
    :return: None
    """
    # 判断时间当超过上班时间则打下班卡。否则则打上班卡。
    if go_hour <= datetime.datetime.now().hour < back_hour:
        # 用来分类上班和下班。作为参数传入任务调度
        hourtype = 1
        print("下次将在", str(back_hour), ":", str(minute), "打卡")
    else:
        hourtype = 2
        print("下次将在", str(go_hour), ":", str(minute), "打卡")
    # 执行任务调度函数
    func(hourtype, minute)


# 任务调度
def start_loop(hourtype, minute):
    """
    每次循环完成，携带生成的随机分钟数来再次进行循环，当打卡后，再重新生成随机数
    :param hourtype: 设置的上班时间点
    :param minute: 随机生成的分钟数（30-55）
    :return: None
    """
    now_time = datetime.datetime.now()
    now_hour = now_time.hour
    now_minute = now_time.minute
    # 上班，不是周末（双休），小时对应，随机分钟对应
    if hourtype == 2 and now_hour == go_hour and now_minute == minute and is_weekend():
        random_time = random_minute()
        DingDing(directory).goto_work(random_time)
        scheduler.enter(0, 0, incode_loop, (start_loop, random_time,))
    if hourtype == 1 and now_hour == back_hour and now_minute == minute and is_weekend():
        random_time = random_minute()
        DingDing(directory).after_work(random_time)
        scheduler.enter(0, 0, incode_loop, (start_loop, random_time,))
    else:
        print(now_hour, ':', now_minute)
        scheduler.enter(60, 0, start_loop, (hourtype, minute,))


# 是否是周末
def is_weekend():
    """
    :return: if weekend return False else return True
    """
    now_time = datetime.datetime.now().strftime("%w")
    if now_time == "6" or now_time == "0":
        return False
    else:
        return True


if __name__ == "__main__":
    pass
    # ======formal
    # scheduler.enter(0, 0, incode_loop, (start_loop, random_minute(),))
    # scheduler.run()
    # ====test
    # image = SendMessage(2).TailorImage("D:\\screen.png")
    # shotmessage = SendMessage(2).baidu_img_str(image)
    # print(shotmessage)
    # SendMessage(shotmessage)
    # SendMessage()
    dingding = DingDing(directory)
    dingding.goto_work()
    # ==== weekend
    print(is_weekend())
