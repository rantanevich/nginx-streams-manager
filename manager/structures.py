from enum import IntEnum
from typing import NamedTuple, Optional


class Route(NamedTuple):
    dst: str
    prefix: int
    gateway: str
    ifindex: Optional[int] = None
    ifname: Optional[str] = None

    def __repr__(self):
        return f'{self.dst}/{self.prefix} via {self.gateway}'


class Address(NamedTuple):
    ip: str
    prefix: int
    ifindex: Optional[int] = None
    ifname: Optional[str] = None

    def __repr__(self):
        return f'{self.ip}/{self.prefix} ({self.ifname})'


# /etc/iproute2/rt_protos
class RTProto(IntEnum):
    UNSPEC = 0
    REDIRECT = 1
    KERNEL = 2
    BOOT = 3
    STATIC = 4


# /etc/iproute2/rt_scopes
class RTScope(IntEnum):
    GLOBAL = 0
    NOWHERE = 255
    HOST = 254
    LINK = 253
