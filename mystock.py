# -*- coding: utf-8 -*-

import os
import sys
import curses
import select
import locale
import urllib2
from config import *

locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

class MyStock(object):
    """
    """
    def __init__(self):
        # 确认配置文件
        path = './my_stock.conf'
        if 1 >= len(sys.argv):
            print 'use default conf!'
        else:
            path = sys.argv[1]
        if 0 == len(path) or not os.path.isfile(path):
            print 'wrong conf path!'
            sys.exit(0)
        my_config = config_module(path)
        self.stock_list = my_config.get_string("stock", "stockid", '')
        if 0 == len(self.stock_list):
            print 'empty stock id'
            sys.exit(0)

        self.per_time = my_config.get_int("stock", "pertime", 1)

    def run(self):
        stdscr = self.init_env()
        self.set_win(stdscr)
        i = 0
        while True:
            infds, outfds, errfds = select.select([0, ], [], [], self.per_time)
            if 0 < len(infds):
                break
            # display_info(stdscr, 'Hola, curses!'+str(i), i+4, 0)
            self.print_stock(stdscr, self.stock_list)
            i += 1
        get_ch_and_continue(stdscr)
        unset_win(stdscr)

    def init_env(self):
        return curses.initscr()

    def set_win(self, stdscr):
        """
        控制台设置
        """
        # 使用颜色首先需要调用这个方法
        curses.start_color()
        # 文字和背景色设置，设置了两个color pair，分别为1和2
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        # 关闭屏幕回显
        curses.noecho()
        # 输入时不需要回车确认
        curses.cbreak()
        # 设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒
        stdscr.nodelay(1)

    def print_stock(self, stdscr, stock_list):
        # stocklist=['sz002276','sz000656','sh601166']
        # stocks=','.join(stocklist)
        url = 'http://hq.sinajs.cn/list='+stock_list

        def getreply(url):
            """
            """
            response = urllib2.urlopen(url)
            html = response.read().decode('gb2312').encode('utf-8')
            return html

        html = getreply(url)
        # print html
        line_list = html.split(';')
        # print line_list

        stock_info_list = []
        for line in line_list:
            line = line[4:-1]
            kvlist = line.split('=')
            if len(kvlist) < 2:
                continue
            # print kvlist
            data_line = kvlist[1]
            data_list = data_line.split(',')
            name = data_list[0][1:100]
            current = data_list[3]
            percent = (float(data_list[3])-float(data_list[2]))/float(data_list[2])*100
            stock_info_list.append((name, current, percent))

        # print '  name     current     percent'
        display_info(stdscr, 'name       current     percent', 0, 0)

        linenb = 1
        sorted_stock = sorted(stock_info_list, None, get_key, True)
        for info in sorted_stock:
            name = info[0]
            current = info[1]
            percent = info[2]
            if len(name) == 3:
                name += '  '
            if percent < 0:
                str_percent = str(percent)[0:5]+'%'
            else:
                str_percent = ' '+str(percent)[0:4]+'%'

            # print name,'  ',current, '   ',str_percent
            my_stock_info = name+'    '+current+'\t'+str_percent
            if '-' == str_percent[0]:
                display_info(stdscr, my_stock_info, linenb, 0, 1)
            else:
                display_info(stdscr, my_stock_info, linenb, 0, 2)
            linenb += 1


def display_info(stdscr, str, x, y, colorpair=1):
    """
    使用指定的colorpair显示文字
    """
    # stdscr.addstr(x, y, '                                                                 ',
    #               curses.color_pair(colorpair))
    stdscr.refresh()
    stdscr.addstr(x, y, str, curses.color_pair(colorpair))
    stdscr.refresh()


def get_ch_and_continue(stdscr):
    """
    演示press any key to continue
    """
    # 设置nodelay，为0时会变成阻塞式等待
    stdscr.nodelay(0)
    # 输入一个字符
    ch = stdscr.getch()
    # 重置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒
    stdscr.nodelay(1)
    return True


def unset_win(stdscr):
    """
    控制台重置
    """
    # 恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）
    curses.nocbreak()
    curses.echo()
    # 结束窗口
    curses.endwin()


def get_key(mytuple):
    return mytuple[2]

if __name__ == '__main__':
    ms = MyStock()
    ms.run()
