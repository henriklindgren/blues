"""
Kibana Blueprint
================

**Fabric environment:**

.. code-block:: yaml

    blueprints:
      - blues.kibana

    settings:
      kibana:
        version: 4.6                   # Version of kibana to install (Required)
        elasticsearch_host: localhost  # Elasticsearch server target (Default: localhost)
        basepath: ""                   # External url prefix (must not end with slash)
        landing_page: discover         # Kibana app to load by default
        plugins:                       # Optional list of plugins to install
          - elasticsearch/marvel/latest

"""
from fabric.decorators import task
from fabric.utils import abort

from refabric.api import run, info
from refabric.context_managers import sudo
from refabric.contrib import blueprints

from . import debian

__all__ = ['start', 'stop', 'restart', 'setup', 'configure', 'install_plugin']

blueprint = blueprints.get(__name__)

start = debian.service_task('kibana', 'start')
stop = debian.service_task('kibana', 'stop')
restart = debian.service_task('kibana', 'restart')

start.__doc__ = 'Start Kibana'
stop.__doc__ = 'Stop Kibana'
restart.__doc__ = 'Restart Kibana'


@task
def setup():
    """
    Install and configure kibana
    """
    install()
    configure()


def install():
    with sudo():
        version = blueprint.get('version', '4.6')
        info('Adding apt repository for {} version {}', 'kibana', version)
        debian.add_apt_repository('https://packages.elastic.co/kibana/{}/debian stable main'.format(version))

        info('Adding apt key for Elastic.co')
        debian.add_apt_key('https://packages.elastic.co/GPG-KEY-elasticsearch')

        info('Installing {} version {}', 'kibana', version)
        debian.apt_get_update()
        debian.apt_get('install', 'kibana')

        # Enable on boot
        debian.add_rc_service('kibana', priorities='defaults 95 10')

        # Install plugins
        plugins = blueprint.get('plugins', [])
        for plugin in plugins:
            info('Installing kibana plugin: "{}" ...', plugin)
            install_plugin(plugin)


@task
def configure():
    """
    Configure Kibana
    """
    context = {
        'elasticsearch_host': blueprint.get('elasticsearch_host', 'localhost'),
        'basepath': blueprint.get('basepath', ''),
        'landing_page': blueprint.get('landing_page', 'discover')
    }
    config = blueprint.upload('./kibana.yml', '/opt/kibana/config/', context)

    if config:
        restart()


@task
def install_plugin(name=None):
    """
    Install a single kibana plugin
    """
    if not name:
        abort('No plugin name given')

    with sudo():
        run('/opt/kibana/bin/kibana plugin --install {}'.format(name))
