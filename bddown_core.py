#!/usr/bin/env python2
#!coding=utf-8

import cookielib
import urllib2
import re
import sys
import os
import json
import getopt
import logging
from time import time

from util import check_url, add_http
from command.config import configure


class BaiduDown(object):
    cookjar = cookielib.LWPCookieJar()
    if os.access(configure.cookies, os.F_OK):
        cookjar.load(configure.cookies)
    opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookjar)
    )
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')
    ]

    def __init__(self, raw_link="", filename="", bdstoken="", fs_id="", uk="", shareid="", timestamp="", sign=""):
        self.filename = filename
        self.bdstoken = bdstoken
        self.fs_id = fs_id
        self.uk = uk
        self.shareid = shareid
        self.timestamp = timestamp
        self.sign = sign
        if raw_link:
            self.initialize(raw_link)

    def _get_json(self, input_code=None, vcode=None):
        url = 'http://pan.baidu.com/share/download?channel=chunlei&clienttype=0&web=1' \
              '&uk=%s&shareid=%s&timestamp=%s&sign=%s&bdstoken=%s%s%s' \
              '&channel=chunlei&clienttype=0&web=1' % \
              (self.uk, self.shareid, self.timestamp, self.sign, self.bdstoken,
               convert_none('&input=', input_code),
               convert_none('&vcode=', vcode))
        post_data = 'fid_list=["%s"]' % self.fs_id
        req = self.opener.open(url, post_data)
        json_data = json.load(req)
        return json_data

    def initialize(self, link):
        info = ShareInfo(link)
        self.filename = info.filename
        self.bdstoken = info.bdstoken
        self.uk = info.uk
        self.shareid = info.shareid
        self.fs_id = info.fs_id
        self.timestamp = info.timestamp
        self.sign = info.sign

    @staticmethod
    def save(img):
        data = urllib2.urlopen(img).read()
        with open(os.path.dirname(os.path.abspath(__file__)) + '/vcode.jpg', mode='wb') as fp:
            fp.write(data)
        print "验证码已经保存至", os.path.dirname(os.path.abspath(__file__))

    @property
    def link(self):
        data = self._get_json()
        logging.debug(data)
        if not data.get('errno'):
            return data.get('dlink').encode('utf-8')
        else:
            vcode = data.get('vcode')
            img = data.get('img')
            self.save(img)
            input_code = raw_input("请输入看到的验证码\n")
            data = self._get_json(vcode=vcode, input_code=input_code)
            if not data.get('errno'):
                return data.get('dlink').encode('utf-8')
            else:
                raise VerificationError("验证码错误\n")


class ShareInfo(object):
    def __init__(self, raw_link):
        self.opener = BaiduDown.opener
        self.bdlink = raw_link
        self.data = self._get_download_page()
        self.filename = ""
        self.bdstoken = ""
        self.fs_id = ""
        self.uk = ""
        self.shareid = ""
        self.timestamp = ""
        self.sign = ""
        self._get_info()

    def _get_download_page(self):
        req = self.opener.open(self.bdlink)
        if 'init' in req.url:
            self._verify_passwd(req.url)
            req = self.opener.open(self.bdlink)
        data = req.read()
        return data

    def _get_info(self):
        pattern = re.compile('server_filename="(.+?)";disk.util.ViewShareUtils.bdstoken="(\w+)";'
                             'disk.util.ViewShareUtils.fsId="(\d+)".+?FileUtils.share_uk="(\d+)";'
                             'FileUtils.share_id="(\d+)";.+?FileUtils.share_timestamp="(\d+)";'
                             'FileUtils.share_sign="(\w+)";', re.DOTALL)
        info = re.search(pattern, self.data)
        if not info:
            raise IndexError("无法获取该分享文件的信息\n")
        self.filename = info.group(1)
        self.bdstoken = info.group(2)
        self.fs_id = info.group(3)
        self.uk = info.group(4)
        self.shareid = info.group(5)
        self.timestamp = info.group(6)
        self.sign = info.group(7)

    def _verify_passwd(self, url):
        pwd = raw_input("请输入提取密码\n")
        data = "pwd=%s&vcode=" % pwd
        url = "%s&t=%d&" % (url.replace('init', 'verify'), int(time()))
        logging.debug(url)
        req = self.opener.open(url, data=data)
        mesg = req.read()
        logging.debug(mesg)
        logging.debug(req.info())
        errno = json.loads(mesg).get('errno')
        if errno == -63:
            self._vcode_handle()
        elif errno == -9:
            raise VerificationError("提取密码错误\n")

    # TODO
    def _vcode_handle(self):
        raise VerificationError("提取密码错误\n")


class VerificationError(Exception):
    pass


class GetFilenameError(Exception):
    pass


convert_none = lambda opt, arg: opt + arg if arg else ""


def download(args):
    limit = configure.limit
    output_dir = configure.dir
    optlist, links = getopt.getopt(args, 'lD', ['limit=', 'dir='])
    for k, v in optlist:
        if k == '--limit':
            limit = v
        elif k == '--dir':
            output_dir = v
    links = filter(check_url, links)    # filter the wrong url
    links = map(add_http, links)        # add 'http://'
    for url in links:
        pan = BaiduDown(url)
        filename = pan.filename
        link = pan.link
        download_command(filename, link, limit=limit, output_dir=output_dir)

    sys.exit(0)


def download_command(filename, link, limit=None, output_dir=None):
    print "\033[32m" + filename + "\033[0m"
    firefox_ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'
    cmd = "aria2c -c -o '%(filename)s' -s5 -x5" \
          " --user-agent='%(useragent)s' --header 'Referer:http://pan.baidu.com/disk/home'" \
          " %(limit)s %(dir)s '%(link)s'" % {
              "filename": filename,
              "useragent": firefox_ua,
              "limit": convert_none('--max-download-limit=', limit),
              "dir": convert_none('--dir=', output_dir),
              "link": link
          }
    os.system(cmd)

if '__main__' == __name__:
    pass
