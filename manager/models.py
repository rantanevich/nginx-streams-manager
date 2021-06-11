import socket
import subprocess
from pathlib import Path

from flask import render_template
from pyroute2 import IPRoute
from pr2modules.netlink.rtnl.rtmsg import rtmsg

from manager import app, db
from manager.structures import Route, Address, RTProto, RTScope


class Stream(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    src_port = db.Column(db.Integer, index=True, unique=True)
    dst_ip = db.Column(db.String(16))
    dst_port = db.Column(db.Integer)
    comment = db.Column(db.String(128))
    enabled = db.Column(db.Boolean)

    stream_conf = Path(app.config['STREAM_CONF'])
    backup_conf = Path(app.config['STREAM_CONF'] + '.bak')

    def __repr__(self):
        return f'<Rule: id={self.id}>'

    def __str__(self):
        src_ip = app.config['SOURCE_IP']
        return (f'{src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}')

    def update(self, **kwargs):
        self.src_port = kwargs.get('src_port')
        self.dst_ip = kwargs.get('dst_ip')
        self.dst_port = kwargs.get('dst_port')
        self.comment = kwargs.get('comment')
        self.enabled = kwargs.get('enabled')

    @classmethod
    def apply_rules(cls):
        rules = cls.query.filter(cls.enabled).all()
        new_conf = render_template('stream.conf', rules=rules)
        cls.backup_conf.write_bytes(cls.stream_conf.read_bytes())
        cls.stream_conf.write_text(new_conf)

        test_conf = subprocess.run('sudo nginx -t',
                                   shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        is_rollback_needed = test_conf.returncode != 0
        if not is_rollback_needed:
            reload_conf = subprocess.run('sudo nginx -s reload',
                                         shell=True,
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
            is_rollback_needed = reload_conf.returncode != 0

        if is_rollback_needed:
            cls.stream_conf.write_bytes(cls.backup_conf.read_bytes())
        return not is_rollback_needed

    @staticmethod
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('127.0.0.1', port)) == 0


class RouteTable:
    '''Manipulates entries in the kernel routing tables'''

    @staticmethod
    def static_routes() -> set:
        '''Returns static routes'''
        with IPRoute() as ipr:
            routes = set()
            for route in ipr.get_routes(table=254, family=socket.AF_INET):
                if route['proto'] in [RTProto.BOOT, RTProto.STATIC]:
                    routes.add(RouteTable.parse_route(route))
            return routes

    @staticmethod
    def onlink_routes() -> set:
        '''Returns onlink routes'''
        with IPRoute() as ipr:
            routes = set()
            for route in ipr.get_routes(table=254, family=socket.AF_INET,
                                        proto=RTProto.KERNEL):
                routes.add(RouteTable.parse_route(route))
            return routes

    @staticmethod
    def add_route(route: Route):
        '''Adds a new static route'''
        with IPRoute() as ipr:
            ipr.route('add', dst=route.dst, mask=route.prefix,
                      gateway=route.gateway)
            ifname = RouteTable.dst_to_ifname(route.dst)
            RouteTable.save_to_disk(ifname)

    @staticmethod
    def delete_route(route: Route):
        '''Deletes the static route'''
        with IPRoute() as ipr:
            ipr.route('del', dst=route.dst, mask=route.prefix)
            RouteTable.save_to_disk(route.ifname)

    @staticmethod
    def route_exists(ipv4: str) -> bool:
        '''Checks if the static route exists'''
        return any(ipv4 == f'{route.dst}/{route.prefix}'
                   for route in RouteTable.static_routes())

    @staticmethod
    def dst_to_ifname(dst: str) -> str:
        '''Finds an interface name with a destination network'''
        with IPRoute() as ipr:
            route = ipr.get_routes(dst=dst)[0]
            return RouteTable.parse_route(route).ifname

    @staticmethod
    def parse_route(route: rtmsg) -> Route:
        '''Parses RTNL message'''
        with IPRoute() as ipr:
            ifindex = route.get_attr('RTA_OIF')
            ifname = ipr.get_links(ifindex)[0].get_attr('IFLA_IFNAME')
            return Route(dst=route.get_attr('RTA_DST'),
                         prefix=route['dst_len'],
                         gateway=route.get_attr('RTA_GATEWAY', 'On-link'),
                         ifindex=ifindex,
                         ifname=ifname)

    @staticmethod
    def save_to_disk(ifname: str):
        '''Saves the current routes into file'''
        routes = [route for route in RouteTable.static_routes()
                  if route.ifname == ifname]
        route_cfg = Path(app.config['ROUTE_CONF'] + ifname)
        content = render_template('route.cfg', routes=routes)
        route_cfg.write_text(content)


class NetworkInterfaces:
    '''Manipulates IPv4 address attached to a network device'''

    @staticmethod
    def addresses() -> set:
        '''Returns addresses attached to network devices'''
        with IPRoute() as ipr:
            addresses = set()
            for address in ipr.get_addr(family=socket.AF_INET, scope=RTScope.GLOBAL):
                addresses.add(Address(ip=address.get_attr('IFA_ADDRESS'),
                                      prefix=address['prefixlen'],
                                      ifindex=address['index'],
                                      ifname=address.get_attr('IFA_LABEL')))
            return addresses

    @staticmethod
    def interfaces() -> list:
        '''Returns names of network devices except loopback'''
        with IPRoute() as ipr:
            ifnames = []
            for link in ipr.get_links()[1:]:
                ifnames.append(link.get_attr('IFLA_IFNAME'))
            return ifnames

    @staticmethod
    def address_exists(ipv4: str) -> bool:
        '''Checks if the address exists'''
        return any(ipv4 == f'{address.ip}/{address.prefix}'
                   for address in NetworkInterfaces.addresses())

    @staticmethod
    def add_address(address: Address):
        '''Attaches a new address to the network interface'''
        with IPRoute() as ipr:
            ifindex = NetworkInterfaces.ifname_to_ifindex(address.ifname)
            ipr.addr('add', index=ifindex, address=address.ip,
                     mask=address.prefix)
            NetworkInterfaces.save_to_disk(address.ifname)

    @staticmethod
    def delete_address(address: Address):
        '''Detaches the address from the network interface'''
        with IPRoute() as ipr:
            ifindex = NetworkInterfaces.ifname_to_ifindex(address.ifname)
            ipr.addr('del', index=ifindex, address=address.ip,
                     mask=address.prefix)
            NetworkInterfaces.save_to_disk(address.ifname)

    @staticmethod
    def ifname_to_ifindex(ifname):
        '''Finds an interface index with an interface name'''
        with IPRoute() as ipr:
            return ipr.link_lookup(ifname=ifname)[0]

    @staticmethod
    def save_to_disk(ifname):
        '''Saves the current interface's addresses into configuration file'''
        addresses = [address for address in NetworkInterfaces.addresses()
                     if address.ifname == ifname]
        interface_cfg = Path(app.config['INTERFACE_CONF'] + ifname)
        content = render_template('interface.cfg', interface=ifname,
                                  addresses=addresses)
        interface_cfg.write_text(content)
