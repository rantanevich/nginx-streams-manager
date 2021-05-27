import socket
import subprocess
from pathlib import Path

from flask import render_template

from forwarder import app, db


class Rule(db.Model):
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
