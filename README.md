# gis-sync
tools to sync data between AIESEC's global information system and the national systems of AIESEC in Germany

# Requirements
* python2.7
* pip
* simple-salesforce & certifi

# Installation (Debian)
* Install requirements
```
apt-get install python-pip
pip install simple-salesforce
pip install certifi
```
* clone source code `cd /opt && git clone https://github.com/AIESECGermany/gis-sync.git`
* add system user to run sync `useradd -s /usr/sbin/nologin gis-sync`
* setup credentials
```
cd /opt/gis-sync
cp credentials_store.example.py credentials_store.py
nano credentials_store.py
```
* `chown -R gis-sync:nogroup /opt/gis-sync`
* `chmod -R 700 /opt/gis-sync`
* setup cronjob `nano /etc/cron.d/gissync`
```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

2-59/10 0-1 * * * gis-sync cd /opt/gis-sync && python sync.py > /dev/null
2-59/10 4-23 * * * gis-sync cd /opt/gis-sync && python sync.py > /dev/null
5 2 * * * gis-sync cd /opt/gis-sync && python sync.py daily > /dev/null
```
* `service cron reload`

## Setup logrotate (Debian)
* `nano /etc/logrotate.d/gis-sync`
```
/opt/gis-sync/expa_sync.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
}
```

## setup munin plugin (Debian)
* `cp /opt/gis-sync/munin/gis-sync /etc/munin/plugins/`
* `chmod +x /etc/munin/plusing/gis-sync`
* add the following lines to the munin-node config (`nano /etc/munin/plugin-conf.d/munin-node`)
```
[gis-sync]
user gis-sync
```
