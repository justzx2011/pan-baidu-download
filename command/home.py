# coding=utf-8
import time
import json
import urlparse

from bddown_core import BaiduDown, download_command
from util import filter_dict_wrapper as filter_dict
from util import bcolor


def home(args):
    url = args[0]
    if 'uk' in url:
        # find uk
        result = urlparse.urlparse(url).query
        query = urlparse.parse_qs(result)
        uk = query.get('uk', [])[0]
        filelist = FileList(uk)
        filelist.download()


class FileList(object):
    def __init__(self, uk):
        self.opener = BaiduDown.opener
        cookie = {c.name: c.value for c in BaiduDown.cookjar}
        self.bdstoken = cookie.get('STOKEN')
        self.page = 1
        self.limit = 20
        self.uk = uk
        # &bdstoken=%(token)s % {'token': token}
        self._url = 'http://pan.baidu.com/pcloud/feed/getsharelist?t=%(unix_time)d&category=0&auth_type=1' \
                    '&request_location=share_home&start=%(index)d&limit=%(limit)d&query_uk=%(uk)s' \
                    '&channel=chunlei&clienttype=0&web=1' % {'unix_time': int(time.time()), 'index': (self.page-1),
                                                             'limit': self.limit, 'uk': self.uk}
        data = json.load(self.opener.open(self._url))
        if data.get('errno', -1):
            raise FetchError('无法抓取该页面')
        total_count = data.get('total_count', 0)
        if not total_count:
            raise IndexError('该用户分享为空')
        self._raw_list = iter(data.get('records', []))
        self.filelist = map(filter_dict, self._raw_list)

    def show(self):
        files = [i.get('server_filename') for i in self.filelist if not i.get('isdir')]
        dirs = [i.get('server_filename') for i in self.filelist if i.get('isdir')]
        dir_len = len(dirs)
        dirs.extend(files)
        for index, filename in enumerate(dirs):
            if index < dir_len:
                print "%s%d %s%s" % (bcolor.OKBLUE, index+1, filename, bcolor.ENDC)
            else:
                print "%s%d %s%s" % (bcolor.OKGREEN, index+1, filename, bcolor.ENDC)

    def next(self):
        self.page += 1
        self._url = 'http://pan.baidu.com/pcloud/feed/getsharelist?t=%(unix_time)d&category=0&auth_type=1' \
                    '&request_location=share_home&start=%(index)d&limit=%(limit)d&query_uk=%(uk)s' \
                    '&channel=chunlei&clienttype=0&web=1' % {'unix_time': int(time.time()), 'index': (self.page-1),
                                                             'limit': self.limit, 'uk': self.uk}
        data = json.load(self.opener.open(self._url))
        if data.get('errno', -1):
            raise FetchError('无法抓取该页面')
        total_count = data.get('total_count', 0)
        if not total_count:
            raise IndexError('该用户分享为空')
        self._raw_list = iter(data.get('records', []))
        self.filelist = map(filter_dict, self._raw_list)

    def download(self):
        # Bug: when input code is directory, may raise a error
        # TODO: download directory
        self.show()
        while True:
            inp = raw_input("请输入想下载的序号（用空格分开，输入a为全部下载，n为下一页）： \n").split()
            seq = filter(lambda n: n.isdigit() or n == 'n' or n == 'a', inp)
            if 'n' in seq:
                self.next()
                self.show()
                continue
            elif 'a' in seq:
                # download all
                seq = range(1, self.limit+1)
            else:
                try:
                    # filter the input greater than limit
                    seq = map(int, filter(lambda n: int(n) <= self.limit and int(n) > 0, seq))
                except ValueError:
                    raise ValueError("输入错误！")
            for i in seq:
                info = self.filelist[i-1]
                pan = BaiduDown(raw_link='', filename=info.get('server_filename', ''), bdstoken=self.bdstoken,
                                fs_id=info.get('fs_id'), uk=self.uk, shareid=info.get('shareid'),
                                timestamp=info.get('time_stamp'), sign=info.get('sign'))
                download_command(pan.filename, pan.link)
            break


class FetchError(Exception):
    pass
