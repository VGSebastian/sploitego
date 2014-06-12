#!/usr/bin/env python
import collections

import socket

import dns.query
import dns.resolver
import dns.reversename
import dns.rdatatype

from canari.maltego.entities import DNSName, MXRecord, NSRecord, IPv4Address, Phrase
from canari.maltego.message import UIMessage, Field

from entities import IPv6Address

import shlex 
from subprocess import Popen, PIPE, STDOUT

__author__ = 'Sebastian Seitz'
__copyright__ = 'Copyright 2014, Sploitego Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Sebastian Seitz'
__email__ = 'sebastian.seitz@vasgard.com'
__status__ = 'Development'

__all__ = [
    'fping'
]


    

 
def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]
 
def fping_alive(target):
    cmd = "fping -q -a -g %s" % target
    res = get_simple_cmd_output(cmd)
    return res.split()
