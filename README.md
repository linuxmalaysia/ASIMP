ASIMP
=========

ASIMP (Ansible System Integrity Management Platform)

This is still work in progress

ansible-galaxy install -r requirements.yml

ansible-playbook -b -K play.yml

For localhost

ansible-playbook --connection=local play-localhost.yml

Roles

- Ubuntu update
- Lynis audit report

Check this https://github.com/ansible-community/ara

Docker for testing ASIMP

https://hub.docker.com/repository/docker/linuxmalaysia/docker-centos-latest-harden/general

27012020 2020
21062019 0618
