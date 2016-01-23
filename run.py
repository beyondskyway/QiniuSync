# coding=utf-8

__version__ = '1.0'

import os
import sys

reload(sys).setdefaultencoding('UTF-8')


import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import RegexMatchingEventHandler
import config
import json
import hashlib
import urllib2


current_dir = os.path.split(os.path.realpath(__file__))[0]


# 根据路径获取文件夹名称
def get_foldername(path):
    path_str, dir_str = os.path.split(path)
    if dir_str is None:
        dir_str = path_str
    return dir_str


# 复制内容到剪切板
def copy_to_clipboard(buf):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(buf, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


class QiniuSync():
    def __init__(self, paths, reg_ignore):
        self.paths = paths
        self.reg_ignore = reg_ignore
        sys.stderr.write(self.summary())
        self.generate_conf()
        self.copy_ignorefile()
        self.observer = Observer()
        # 初次同步，生成对比库
        for path in config.WATCH_PATH:
            qiniu_syn(path)
        self.start_watch()

    # 生成配置文件
    def generate_conf(self):
        for path in self.paths:
            # 根据路径获取文件夹名称
            dir_str = get_foldername(path)
            json_data = {}
            json_data["src"] = str(path)
            json_data["dest"] = 'qiniu:access_key=' + config.QINIU_ACCESS_KEY + \
                                '&secret_key=' + config.QINIU_SECRET_KEY + \
                                '&bucket=' + config.QINIU_BUCKET + \
                                '&key_prefix=' + dir_str + '/'
            json_data["debug_level"] = 1
            # 根据路径生成文件名
            filename = str(hashlib.md5(path).hexdigest()) + '.json'
            # 文件不存在则重新创建配置文件
            if not os.path.isfile(filename):
                with open(filename, 'w') as f:
                    f.write(json.dumps(json_data))

    # 拷贝屏蔽文件到同步目录(.qrsignore.txt)
    def copy_ignorefile(self):
        src = file(current_dir + '\.qrsignore.txt', 'r+')
        for path in self.paths:
            des_path = path + '/.qrsignore.txt'
            if not os.path.isfile(des_path):
                des = file(des_path, 'w+')
                des.writelines(src.read())
                des.close()
            else:
                continue
        src.close()

    # 启动监控
    def start_watch(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', filename='log.txt')
        # 根据路径创建多个监视对象
        paths = self.paths
        for path in paths:
            event_handler = QiniuSyncEventHandler(path, self.reg_ignore)
            watch = self.observer.schedule(event_handler, path, recursive=True)
            logging_handler = LoggingEventHandler()
            # 为watch添加log处理程序
            self.observer.add_handler_for_watch(logging_handler, watch)
        self.observer.start()
        self.sys_tray()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    # 停止监控
    def stop_watch(self):
        self.observer.stop()
        exit()

    # 最小化
    def sys_tray(self):
        import itertools, glob
        from sys_tray_icon import SysTrayIcon
        # 获取图标
        icons = itertools.cycle(glob.glob('*.ico'))
        # 最小化显示文字
        hover_text = "QiniuSync"
        import ctypes
        import win32con
        wnd = ctypes.windll.kernel32.GetConsoleWindow()
        if wnd != 0:
            ctypes.windll.user32.ShowWindow(wnd, win32con.SW_HIDE)
            ctypes.windll.kernel32.CloseHandle(wnd)

        # 退出处理
        def quit_sync():
            self.stop_watch()
        # 最小化到托盘
        SysTrayIcon(icons.next(), hover_text, menu_options=(), on_quit=quit_sync, default_menu_index=1, wnd=wnd)

    # 输出信息
    def summary(self):
        info = ''
        info += '------------------------------------------------------\n'
        info += 'QiniuSync Version  : %s (python/%s)\n' % (__version__, sys.version[:5])
        info += 'Author             : skywatcher\n'
        info += '------------------------------------------------------\n'
        return info


# 执行同步
def qiniu_syn(path):
    filename = str(hashlib.md5(path).hexdigest()) + '.json'
    cmd = current_dir + '\qrsync.exe ' + current_dir + '\\' + filename
    os.system(cmd)


# 监听文件变动，正则过滤文件
class QiniuSyncEventHandler(RegexMatchingEventHandler):
    def __init__(self, path, reg_ignore = []):
        super(QiniuSyncEventHandler, self).__init__(ignore_regexes=reg_ignore,ignore_directories=True)
        self.path = path

    def on_any_event(self, event):
        qiniu_syn(self.path)
        # 根据路径获取文件夹名称
        dir_str = get_foldername(self.path)
        # 生成链接
        src_path = event.src_path
        url = config.QINIU_DOMIAN + (dir_str + src_path.replace(self.path, '')).replace('\\', urllib2.quote('/'))
        copy_to_clipboard(url)

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass


if __name__ == "__main__":
    qs = QiniuSync(config.WATCH_PATH, config.FILE_FILTER)
