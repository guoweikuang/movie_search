#!/usr/bin/env python3
# coding:utf-8
import sys
from multiprocessing import Pool, Manager
from bs4 import BeautifulSoup
import time, random, requests, sqlite3, os

server = Manager()
host = 'http://www.80s.tw'
screen = server.dict(
    {'label': 'NONE', 'url': 'http://baidu.com', 'title': 'none', 'IMG': 'none', 'detail': 'none', 'link': 'none',
     'index': 0, 'total': 10})


def mLog(opt):
    os.system('clear')
    print('\033[41;30m MESSAGE: %s\033[m' % opt['label'])
    print('\033[46;30m PATH: %10s\033[m\n' % opt['url'])

    print('\033[0;35m TITLE\033[m:\t%s' % opt['title'])
    print('\033[0;35m IMG\033[m:\t%s' % opt['IMG'][:30] + '...')
    print('\033[0;34m DETAIL\033[m:%s' % opt['detail'][:60] + '...')
    print('\033[0;36m LINK\033[m:\t%s' % opt['link'][:60] + '...')

    bar_status = opt['index'] * 40 / opt['total']
    status = opt['index'] * 100 / opt['total']
    print('\n[%-40s]%s(%d/%d)' % ('>' * bar_status, str(status) + '%', opt['index'], opt['total']))


class domPa(object):
    def __init__(self, path, section='a', title='.title', img='.img', detail='.detail'):
        self.path = path
        self.page = requests.get(host + path)
        self.status = self.page.status_code
        self.section = section
        self.img = img
        self.title = title
        self.detail = detail
        self.dom = BeautifulSoup(self.page.text, 'lxml')
        self.p = Pool(5)

    def run(self):
        screen['url'] = self.path
        screen['label'] = self.status
        screen['total'] = len(self.dom.find('ul', class_="me1 clearfix").find_all('li'))
        mLog(screen)
        result = []
        for e in self.dom.find('ul', class_="me1 clearfix").find_all('li'):
            result.append(self.p.apply_async(botTask, (e,)))
            # self.botTask(i,e)
        self.p.close()
        self.p.join()
        print(result)
        for res in result:

            for e in res.get():
                dat = (e[0], e[1], e[2], e[3])
                try:
                    db.execute('INSERT INTO movies VALUES(?,?,?,?)', dat)
                except Exception as e:
                    screen['label'] = '*************SAME LINK!************'
                    mLog(screen)
        db.commit()


def botTask(e):
    dom_title_path_img = e.find('a')
    movieName = dom_title_path_img.find('img').get('alt')
    print(movieName)
    screen['title'] = movieName
    movieImg = dom_title_path_img.find('img').get('_src')
    screen['IMG'] = movieImg
    movieDetail = e.find('span', class_="tip").get_text().strip()
    screen['detail'] = movieDetail[:50] + '...'

    urll = host + dom_title_path_img.get('href')
    pagee = requests.get(urll)
    dom = BeautifulSoup(pagee.text, 'lxml')
    datas = []
    for ee in dom.find_all('span', class_="xunlei dlbutton1").find('a'):
        movieLink = ee.get('href')
        screen['link'] = movieLink
        mLog(screen)
        # robLog(i, 'Got it ! [%s]@ %s' % (movieName, movieLink))
        datas.append([movieName, movieLink, movieDetail, movieImg])

    # end = time.time()
    # robLog(i, 'Task done! Cost %0.2fs' % (end-start), '\033[0;36m')
    screen['index'] += 1
    return (datas)


# mLog(u'but0n,I\'m Running!')
# mLog('Connect Database...')
screen['label'] = 'Connect Database...'
db = sqlite3.connect('mv.db')

if db:
    try:
        db.execute('CREATE TABLE movies(name TEXT, link TEXT PRIMARY KEY, detail TEXT, img TEXT)')
        screen['label'] = 'CREATE TABLE...'
        mLog()
    finally:
        i = 1
        while i:
            print('下载开始')
            bug = domPa('/movie/list/')
            if bug.status == 200:
                screen['index'] = 0
                screen['label'] = 'HTTP Connect Succeed! To [p' + str(i) + ']'
                mLog(screen)
                i += 1
                bug.run()
            else:
                screen['label'] = 'Checkout your network!'
                mLog(screen)
            i = 0

        db.close()
        mLog('DONE')

