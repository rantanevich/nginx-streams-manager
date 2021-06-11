import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
basedir = Path(__file__).parent


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')

    SOURCE_IP = os.getenv('SOURCE_IP')
    STREAM_CONF = '/etc/nginx/stream.conf'

    ROUTE_CONF = '/etc/sysconfig/network-scripts/route-'
    INTERFACE_CONF = '/etc/sysconfig/network-scripts/ifcfg-'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
                              f'sqlite:///{basedir / "app.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
