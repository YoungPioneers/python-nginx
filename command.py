#!/usr/bin/env python
# encoding: utf-8
#
#  Author:   huangjunwei@youmi.net
#  Time:     Tue 20 Jan 2015 05:57:56 PM HKT
#  File:     nginx/command.py
#  Desc:     commands about nginx
#
from fabric.api import run, env, sudo


# more nice to use ansible
def _nginx_command(command, bin=None, config=None, is_sudo=True):
    if bin is None:
        bin = env.nginx_bin

    if config is None:
        config = env.nginx_config

    if "reload" == command:
        cmd = "%(bin)s -s reload" % locals()
    elif "start" == command:
        cmd = "%(bin)s -c %(config)s" % locals()
    elif "stop" == command:
        cmd = "%(bin)s -s stop" % locals()

    if is_sudo:
        sudo(cmd)
    else:
        run(cmd)


def reload(bin=None, is_sudo=False):
    _nginx_command("reload", bin=bin, is_sudo=sudo)


def start(bin=None, config=None, is_sudo=True):
    _nginx_command("start", bin=bin, config=config, is_sudo=is_sudo)


def stop(bin=None, is_sudo=False):
    _nginx_command("stop", bin=bin, is_sudo=sudo)
