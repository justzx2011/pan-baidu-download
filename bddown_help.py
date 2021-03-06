#!/usr/bin/env python2
#!coding=utf-8

basic_command = [
    ('help',        'Show this help'),
    ('login',       'Login using Baidu account'),
    ('download',    'Download file from the Baidu pan link'),
    ('show',        'Show the Baidu pan real link and filename'),
    ('export',      'export link to aria2 json-rpc'),
    ('config',      'save configuration to file')
]

extended_usage = ''


def join_commands(command):
    n = max(len(x[0]) for x in command)
    n = max(n, 10)
    return ''.join(' %%-%ds %%s\n' % n % (h, k) for (h, k) in basic_command)

basic_usage = '''python bddown_cli.py <command> [<args>]

Basic commands:
''' + join_commands(basic_command)


def usage():
    return basic_usage + '''
Use 'python bddown_cli.py help' for details
Use 'python bddown_cli.py help <command>' for more information on a specific command.
Check https://github.com/banbanchs/pan-baidu-download for details'''


def show_help():
    return ''' Python script for Baidu pan
Basic usage:
    ''' + basic_usage + extended_usage + '\n'

login = '''python bddown_cli.py login [username] [password]

Baidu login.

Example:
  python bddown_cli.py login XXXXX 123456
  python bddown_cli.py login xxx@qq.com 123456
'''

download = '''python bddown_cli.py download [options] [Baidupan-url]...

Download file from the Baidu pan link

Options:
    --limit=[speed]             Max download speed limit.
    --dir=[dir]                 Download task to dir.
    --secret=[string]           Retrieval password'''

show = '''python bddown_cli.py show [Baidupan-url]...

Show the real download link and filename

Example:
 python bddown_cli.py show http://pan.baidu.com/s/15lliC
'''

export = '''python bddown_cli.py export [Baidupan-url]...

export link to aria2 json-rpc

Example:
  python bddown_cli.py show http://pan.baidu.com/s/15lliC
'''

config = '''python bddown_cli.py config key [value]

save configuration to config.ini

Examples:
 python bddown_cli.py config username XXXXX
 python bddown_cli.py config password 123456
 python bddown_cli.py config limit 500k
 python bddown_cli.py config dir /home/john/Downloads
 python bddown_cli.py config save_vcode 1
'''

help_help = '''Get helps:
 python bddown_cli.py help help
 python bddown_cli.py help download
 python bddown_cli.py help show
 python bddown_cli.py help <command>'''

help = help_help
