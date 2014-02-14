# coding=utf-8
import time
import json

from bddown_core import BaiduDown
from util import filter_dict_wrapper as filter_dict
from util import bcolor


def home(args):
    url = args[0]
    if 'uk' in url:
        # find uk
        uk = (lambda s: s[35:]if s.find('#') == -1 else s[35:s.find('#')])(url)
        filelist = FileList(uk)
        filelist.show()


class FileList(object):
    def __init__(self, uk):
        self.opener = BaiduDown.opener
        self.uk = uk
        # &bdstoken=%(token)s % {'token': token}
        self._url = 'http://pan.baidu.com/pcloud/feed/getsharelist?t=%(unix_time)d&category=0&auth_type=1' \
                    '&request_location=share_home&start=0&limit=20&query_uk=%(uk)s' \
                    '&channel=chunlei&clienttype=0&web=1' % {'unix_time': int(time.time()), 'uk': self.uk}
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
                print "%s%d %s%s" % (bcolor.OKBLUE, index, filename, bcolor.ENDC)
            else:
                print "%s%d %s%s" % (bcolor.OKGREEN, index, filename, bcolor.ENDC)

    def download(self):
        pass


class FetchError(Exception):
    pass

