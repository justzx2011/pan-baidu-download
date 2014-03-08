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
        self.limit = 40
        self.uk = str(uk)
        # &bdstoken=%(token)s % {'token': token}
        self._url = 'http://pan.baidu.com/pcloud/feed/getsharelist?t=%(unix_time)d&category=0&auth_type=1' \
                    '&request_location=share_home&start=%(index)d&limit=%(limit)d&query_uk=%(uk)s' \
                    '&channel=chunlei&clienttype=0&web=1' % {'unix_time': int(time.time()), 'index': (self.page - 1),
                                                             'limit': self.limit, 'uk': self.uk}
        data = json.load(self.opener.open(self._url))
        if data.get('errno', -1):
            raise FetchError('无法抓取该页面')
        total_count = data.get('total_count', 0)
        if not total_count:
            raise IndexError('该用户分享为空')
        self._raw_list = data.get('records', [])

    def __len__(self):
        return len(self._raw_list)

    def show(self):
        for index, item in enumerate(self._raw_list):
            # if is dir or set
            if item.get('filecount') > 1 or item.get('dir_cnt'):
                print "%s%2d %s%s" % (bcolor.OKBLUE, index + 1, item.get('title'), bcolor.ENDC)
            else:
                print "%s%2d %s%s" % (bcolor.OKGREEN, index + 1, item.get('title'), bcolor.ENDC)

    def next(self):
        self.page += 1
        self._url = 'http://pan.baidu.com/pcloud/feed/getsharelist?t=%(unix_time)d&category=0&auth_type=1' \
                    '&request_location=share_home&start=%(index)d&limit=%(limit)d&query_uk=%(uk)s' \
                    '&channel=chunlei&clienttype=0&web=1' % {'unix_time': int(time.time()), 'index': (self.page - 1),
                                                             'limit': self.limit, 'uk': self.uk}
        data = json.load(self.opener.open(self._url))
        if data.get('errno', -1):
            raise FetchError('无法抓取该页面')
        total_count = data.get('total_count', 0)
        if not total_count:
            raise IndexError('该用户分享为空')
        self._raw_list = data.get('records', [])

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
                seq = range(1, self.limit + 1)
            else:
                try:
                    # filter the input greater than limit
                    seq = [int(i) for i in seq if self.limit >= len(self) >= int(i)]
                except ValueError:
                    raise ValueError("输入错误！")

            # parser json and download it
            for i in seq:
                info = filter_dict(self._raw_list[i - 1])
                print info
                # if share type is album
                if info.has_key('operation'):
                    for t in info.get('operation'):
                        filelist = t.get('filelist')
                        if not filelist:
                            continue
                        download_seq = [value for f in filelist for (key, value) in f.items()
                                        if key in ['server_filename', 'dlink']]
                        for j in range(len(download_seq) / 2):
                            dlink = download_seq.pop()
                            server_filename = download_seq.pop()
                            download_command(server_filename, dlink)
                # if share type is not a dir
                elif info.has_key('filelist'):
                    shareid = info.get('shareid')
                    for fl in info.get('filelist'):
                        pan = BaiduDown(filename=fl.get('server_filename'), bdstoken=self.bdstoken,
                                        fs_id=fl.get('fs_id'),
                                        uk=self.uk, shareid=shareid, timestamp=fl.get('time_stamp'),
                                        sign=fl.get('sign'))
                        download_command(pan.filename, pan.link)
                # TODO: support dir download
            break


class FetchError(Exception):
    pass
