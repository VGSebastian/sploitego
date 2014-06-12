#!/usr/bin/env python

from canari.maltego.entities import DNSName, Location, Netblock, Phrase, IPv4Address
from canari.framework import configure

from common.fping import fping_alive

__author__ = 'Sebastian Seitz'
__copyright__ = 'Copyright 2014, Sploitego Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Sebastian Seitz'
__email__ = 'sebastian.seitz@vasgard.com'
__status__ = 'Development'

__all__ = [
    'dotransform'
]


@configure(
    label='NetblockToIPs [fping]',
    description='This transform gets all alive hosts in a Netblock using fping.',
    uuids=[ 'sploitego.v2.NetblockToIPv4Address_Ping' ],
    inputs=[ ( 'Reconnaissance', Netblock ) ],
)
def dotransform(request, response):
    target = request.value.replace(' - ', ' ')
    result = fping_alive(target)
    for ip in result:
        response += IPv4Address(ip)
    return response
