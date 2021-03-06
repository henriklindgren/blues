"""
User Utils
==========

Debian user helpers for other blueprints to use.
"""
import os

from fabric.contrib import files

from refabric.contrib import templates
from refabric.context_managers import sudo

from . import debian


def create_system_user(name, groups=None, home=None):
    """
    Create a system user/group with a low UID, starting at 999 and counting downwards.
    Extra groups to join will not be created.

    :param name: Username
    :param home: Home dir path to set and create *(Optional)*
    :param groups: Existing extra groups to join *(Optional)*
    """
    with sudo():
        # Create user, not home dir
        debian.useradd(name, home=home or '/dev/null', create_home=bool(home), shell='/bin/bash',
                       user_group=True, groups=groups, system=True)

        # Create ~/.ssh dir
        create_ssh_path(name)


def create_service_user(name, groups=None, home=None):
    """
    Create a service user/group with a low UID, starting at 100 and counting upwards.
    Home dir and extra groups to join will not be created.

    :param name: Username
    :param home: Home dir path (will not be created) *(Optional)*
    :param groups: Existing extra groups to join *(Optional)*
    """
    with sudo():
        # Create user, not home dir
        debian.useradd(name, home=home or '/dev/null', shell='/bin/false',
                       user_group=True, groups=groups, uid_min=100, uid_max=499)


def create_ssh_path(username):
    user = debian.get_user(username)
    ssh_path = os.path.join(user['home'], '.ssh')
    debian.mkdir(ssh_path, owner=username, group=username)
    debian.chmod(ssh_path, mode=700)


def upload_ssh_keys(username, key_pair_path):
    user = debian.get_user(username)
    ssh_path = os.path.join(user['home'], '.ssh')
    templates.upload(key_pair_path, ssh_path, user=username)
    # Ensure security
    debian.chmod(ssh_path, mode=600, owner=username, group=username, recursive=True)
    debian.chmod(ssh_path, mode=700)


def set_strict_host_checking(username, host, check=False):
    user = debian.get_user(username)
    with sudo(username):
        filename = os.path.join(user['home'], '.ssh', 'config')
        value = 'yes' if check else 'no'
        lines = [
            'Host {}'.format(host),
            '\tStrictHostKeyChecking {}'.format(value)
        ]
        files.append(filename, lines, shell=True)
