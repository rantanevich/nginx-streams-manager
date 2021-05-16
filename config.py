import os
from pathlib import Path


basedir = Path(__file__).parent


class Config:
    SOURCE_IP = os.getenv('SOURCE_IP')
    NGINX_CONF = '/etc/nginx/nginx.conf'

    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
                              f'sqlite:///{basedir / "app.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
