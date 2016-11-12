# coding: utf-8
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager
import sqlite3
import os


host = 'http://www.80s.tw'
# server = Manager()
# screen = server.dict({'label': 'NONE', 'url': 'http://baidu.com', 'title': 'none',\
#                       'IMG': 'none', 'detail': 'none', 'link': 'none', 'index': 0, 'total': 10})
# screen = dict({'label': 'NONE', 'url': 'http://baidu.com', 'title': 'none',\
#                       'IMG': 'none', 'detail': 'none', 'link': 'none', 'index': 0, 'total': 10})


def botTask(e, screen):
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
    movieLink = dom.find('span', class_="xunlei dlbutton1").find('a').get('href')
    datas.append([movieName, movieLink, movieDetail, movieImg])
    mLog(screen)
    screen['index'] += 1
    return (datas)


# def crawl_page():
#     html = requests.get(host+path)
#     soup = BeautifulSoup(html.content, 'lxml')
#     screen['url'] = path
#     screen['label'] = html.status_code
#     screen['total'] = len(soup.find('ul', class_="me1 clearfix").find_all('li'))
#     result = []
#     for e in soup.find('ul', class_="me1 clearfix").find_all('li'):
#         main(result, e)
#         result.append(p.apply_async(botTask, (e,)))
def mLog(opt):
    os.system('clear')
    print('\033[41;30m MESSAGE: %s\033[m' % opt['label'])
    print('\033[46;30m PATH: %10s\033[m\n' % opt['url'])

    print('\033[0;35m TITLE\033[m:\t%s' % opt['title'])
    print('\033[0;35m IMG\033[m:\t%s' % opt['IMG'][:30]+'...')
    print('\033[0;34m DETAIL\033[m:%s' % opt['detail'][:60]+'...')
    print('\033[0;36m LINK\033[m:\t%s' % opt['link'][:60]+'...')

    bar_status = opt['index']*40/opt['total']
    status = opt['index']*100/opt['total']
    print('\n[%-40s]%s(%d/%d)' % ('>'*bar_status, str(status)+'%', opt['index'], opt['total']))


def create_db(db, screen):
    if db:
        try:
            db.execute('CREATE TABLE movies(name text, link text primary key, detail text, img text)')
            screen['label'] = 'CREATE TABLE...'
            mLog()
        except Exception as e:
            print(e)


def save_db(db, result):
    for e in result:
        for j in e.get():
            dat = (j[0], j[1], j[2], j[3])
            try:
                db.execute('INSERT INTO movies VALUES(?,?,?,?)', dat)
            except Exception as e:
                print(e)
                mLog(screen)
    db.commit()


def get_page_content(path):
    host = 'http://www.80s.tw'
    return requests.get(host+path)

if __name__ == '__main__':
    server = Manager()
    screen = server.dict({'label': 'NONE', 'url': 'http://baidu.com', 'title': 'none', \
                          'IMG': 'none', 'detail': 'none', 'link': 'none', 'index': 0, 'total': 10})
    db = sqlite3.connect('mv.db')
    i = 1
    create_db(db, screen)
    while i:

        path = '/movie/list/-----p' + str(i)

        html = get_page_content(path)
        soup = BeautifulSoup(html.content, 'lxml')
        screen['url'] = path
        screen['label'] = html.status_code
        screen['total'] = len(soup.find('ul', class_="me1 clearfix").find_all('li'))
        result = []
        p = Pool(8)
        for e in soup.find('ul', class_="me1 clearfix").find_all('li'):
            result.append(p.apply_async(botTask, (e, screen)))
        print('===' * 40)
        save_db(db, result)
        i += 1



# class domPa(object):
#     def __init__(self, path, section='a', title='.title', img='.img', detail='.detail'):
#         self.path = path
#         self.page = requests.get(host+path)
#         self.status = self.page.status_code
#         self.section = section
#         self.img = img
#         self.title = title
#         self.detail = detail
#         self.dom = BeautifulSoup(self.page.text, 'html.parser')
#         self.p = Pool(5)
#
#     def run(self):
#         screen['url'] = self.path
#         screen['label'] = self.status
#         screen['total'] = len(self.dom.select('.me1.clearfix')[0].select('li'))
#         # mLog(screen)
#         result = []
#         for e in self.dom.select('.me1.clearfix')[0].select('li'):
#                 result.append(self.p.apply_async(botTask, (e,)))
#                 # self.botTask(i,e)
#         self.p.close()
#         self.p.join()
#
#
# def botTask(e):
#     dom_title_path_img = e.select('a')[0]
#     movieName = dom_title_path_img.get('title')
#     screen['title'] = movieName
#     movieImg = dom_title_path_img.select('img')[0].get('_src')[2:]
#     screen['IMG'] = movieImg
#     movieDetail = e.select('.tip')[0].get_text().strip()
#     screen['detail'] = movieDetail[:50]+'...'
#
#
#     urll = host + dom_title_path_img.get('href')
#     pagee = requests.get(urll)
#     dom = BeautifulSoup(pagee.text, 'html.parser')
#     datas = []
#     for ee in dom.select('span.xunlei')[0].select('a'):
#         movieLink = ee.get('href')
#         screen['link'] = movieLink
#         mLog(screen)
#         # robLog(i, 'Got it ! [%s]@ %s' % (movieName, movieLink))
#         datas.append([movieName, movieLink, movieDetail, movieImg])
#
#     # end = time.time()
#     # robLog(i, 'Task done! Cost %0.2fs' % (end-start), '\033[0;36m')
#     screen['index'] += 1
#     return (datas)
#
# if __name__ == '__main__':
#     path = '/movie/list/'
#     server = Manager()
#     screen = server.dict({'label': 'NONE', 'url': 'http://baidu.com', 'title': 'none', \
#                           'IMG': 'none', 'detail': 'none', 'link': 'none', 'index': 0, 'total': 10})
#     screen['url'] = path
#     screen['label'] = self.status
#     screen['total'] = len(dom.select('.me1.clearfix')[0].select('li'))
#     # mLog(screen)
#     result = []
#     for e in self.dom.select('.me1.clearfix')[0].select('li'):
#         result.append(self.p.apply_async(botTask, (e,)))
#         # self.botTask(i,e)
#     self.p.close()
#     self.p.join()
#     tf = domPa(path)