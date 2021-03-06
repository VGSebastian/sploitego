# !/usr/bin/env python

import subprocess
from canari.maltego.utils import debug

from canari.utils.fs import cookie
from canari.config import config
from scapy.all import conf

from ctypes import Structure, c_ubyte, c_uint32, c_uint16, addressof, sizeof, POINTER, string_at, c_char_p, cast
from socket import socket, AF_UNIX, AF_INET, AF_INET6, inet_pton
import os
from numbers import Number


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Sploitego Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'P0fMagic',
    'P0fStatus',
    'P0fAddr',
    'P0fMatch',
    'P0fError',
    'fingerprint'
]


class P0fApiQuery(Structure):
    _fields_ = [
        ('magic', c_uint32),
        ('addr_type', c_ubyte),
        ('addr', c_ubyte * 16)
    ]


class P0fApiResponse(Structure):
    _fields_ = [
        ('magic', c_uint32),
        ('status', c_uint32),
        ('first_seen', c_uint32),
        ('last_seen', c_uint32),
        ('total_conn', c_uint32),
        ('uptime_min', c_uint32),
        ('up_mod_days', c_uint32),
        ('last_nat', c_uint32),
        ('last_chg', c_uint32),
        ('distance', c_uint16),
        ('bad_sw', c_ubyte),
        ('os_match_q', c_ubyte),
        ('os_name', c_ubyte * 32),
        ('os_flavor', c_ubyte * 32),
        ('http_name', c_ubyte * 32),
        ('http_flavor', c_ubyte * 32),
        ('link_type', c_ubyte * 32),
        ('language', c_ubyte * 32),
    ]


class P0fMagic:
    Query = 0x50304601
    Response = 0x50304602


class P0fStatus:
    BadQuery = 0x00
    OK = 0x10
    NoMatch = 0x20


class P0fAddr:
    IPv4 = 0x04
    IPv6 = 0x06


class P0fMatch:
    Fuzzy = 0x01
    Generic = 0x02


class P0fError(Exception):
    pass


def fingerprint(ip):
    iface = conf.route.route(ip)[0]
    us = cookie('.sploitego.p0f.%s.sock' % iface)

    if not os.path.exists(us):
        log = cookie('.sploitego.p0f.%s.log' % iface)
        cmd = os.path.join(config['p0f/path'], 'p0f')
        fpf = os.path.join(config['p0f/path'], 'p0f.fp')
        p = subprocess.Popen(
            [cmd, '-d', '-s', us, '-o', log, '-f', fpf, '-i', iface, '-u', 'nobody'],
            stdout=subprocess.PIPE
        )
        debug(*p.communicate()[0].split('\n'))
        debug(
            "!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!",
            "! IF THIS TRANSFORM IS STILL RUNNING THEN SHUT IT DOWN AND  !",
            "! TRY AGAIN! THERE IS A BUG IN MALTEGO THAT DOES NOT        !",
            "! TERMINATE TRANSFORMS IF A TRANSFORM SPAWNS A CHILD        !",
            "! PROCESS. PLEASE BUG SUPPORT@PATERVA.COM FOR A FIX.        !",
            "!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!",
        )
        if p.returncode:
            raise P0fError('Could not locate or successfully execute the p0f executable.')
        return {'status': P0fStatus.NoMatch}

    r = P0fApiQuery()
    r.magic = P0fMagic.Query

    if ':' in ip:
        r.addr_type = P0fAddr.IPv6
        ip = inet_pton(AF_INET6, ip)
    else:
        r.addr_type = P0fAddr.IPv4
        ip = inet_pton(AF_INET, ip)

    for i, a in enumerate(ip):
        r.addr[i] = ord(a)

    s = socket(AF_UNIX)
    s.connect(us)
    s.send(string_at(addressof(r), sizeof(r)))
    data = c_char_p(s.recv(sizeof(P0fApiResponse)))
    pr = cast(data, POINTER(P0fApiResponse)).contents
    s.close()

    if pr.status == P0fStatus.BadQuery:
        raise P0fError('P0f could not understand the query.')

    return dict(
        (
            fn,
            getattr(pr, fn) if isinstance(getattr(pr, fn), Number) else string_at(getattr(pr, fn))
        ) for fn, ft in pr._fields_
    )