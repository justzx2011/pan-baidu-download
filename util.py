#!/usr/bin/env python2
#!coding=utf-8

import bddown_help

URL = ['pan.baidu.com', 'yun.baidu.com']


def bd_help(args):
    if len(args) == 1:
        helper = getattr(bddown_help, args[0].lower(), bddown_help.help)
        usage(helper)
    elif len(args) == 0:
        usage(bddown_help.show_help)
    else:
        usage(bddown_help.help)


def usage(doc=bddown_help.usage, message=None):
    if hasattr(doc, '__call__'):
        doc = doc()
    if message:
        print message
    print doc.strip()


def check_url(raw_url=""):
    raw_url.lower()
    if raw_url.startswith('http://'):
        raw_url = raw_url[7:]
    rev = raw_url.rstrip('/').split('/')
    if rev[0] in URL and len(rev) > 1:
        return True
    return False

add_http = lambda url: url if url.startswith('http://') else 'http://'+url


# from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# THANKS!

class BColor(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

bcolor = BColor()

