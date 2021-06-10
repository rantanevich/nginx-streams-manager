# nginx-streams-manager

It's Web UI to manage Nginx streams with a simple interface.



## Requirements

* RHEL / CentOS 7
* Python 3.6+
* Nginx (ngx_stream_core_module is enabled)



## Installation

### Ansible

Prepare a server and install the latest version:
```sh
# without HTTP(s) proxy
ansible-playbook -i srv-app-01, deploy/main.yml -e ansible_user=sshuser

# with HTTP(s) proxy
ansible-playbook -i srv-app-01, deploy/main.yml \
                 -e ansible_user=sshuser \
                 -e http_proxy='http://user:pass@host:port' \
                 -e https_proxy='http://user:pass@host:port'
```

Updating:
```sh
# without HTTP(s) proxy
ansible-playbook -i srv-app-01, deploy/deploy.yml -e ansible_user=sshuser

# with HTTP(s) proxy
ansible-playbook -i srv-app-01, deploy/deploy.yml \
                 -e ansible_user=sshuser \
                 -e http_proxy='http://user:pass@host:port' \
                 -e https_proxy='http://user:pass@host:port'
```

### Manual

Clone repository:
```sh
git clone https://github.com/rantanevich/nginx-streams-manager.git
```

Install via pip/pipenv:
```sh
# pip
pip install -r requirements.txt

# pipenv
pipenv install --ignore-pipfile
```

Apply DB migrations
```sh
export FLASK_APP=server.py
export DATABASE_URL=sqlite:///app.db

flask db upgrade
```

Linux settings:
```
useradd --create-home --user-group --shell /bin/bash gunicorn
echo "gunicorn ALL=(root) NOPASSWD: $(which nginx) -t, $(which nginx) -s reload" | tee /etc/sudoers.d/gunicorn

cp deploy/gunicorn.{service,socket} /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn.service
systemctl start gunicorn.service

chmod o+x /home/gunicorn
touch /etc/nginx/stream.conf{,.bak}
chgrp gunicorn /etc/nginx/stream.conf{,.bak}
chmod 664 /etc/nginx/stream.conf{,.bak}
cp deploy/nginx.conf /etc/nginx
cp deploy/gunicorn.conf /etc/nginx/conf.d/
nginx -t && nginx -s reload
```

Environment variables:

| Variable     | Required | Example          | Comments                                |
|--------------|----------|------------------|-----------------------------------------|
| SOURCE_IP    | yes      | 192.168.0.1      | IP address of external interface.       |
| SECRET_KEY   | yes      | a9db20d4650      | It uses for any security related needs. |
| DATABASE_URL | yes      | sqlite:///app.db | Database connection parameters.         |



## Usage

![plot](./docs/index.jpg)

![plot](./docs/adding.jpg)

![plot](./docs/editing.jpg)
