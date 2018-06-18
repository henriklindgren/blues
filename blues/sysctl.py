"""
BIND Blueprint
===============

**Fabric environment:**

.. code-block:: yaml

    blueprints:
      - blues.sysctl

    settings:
      params:
        - 'vm.swappiness = 5'

"""
import os
from time import time

from fabric.context_managers import cd, settings
from fabric.contrib import files
from fabric.decorators import task, parallel
from fabric.api import put,env,local

from refabric.context_managers import sudo, silent, hide_prefix
from refabric.contrib import blueprints
from refabric.operations import run
from refabric.utils import info

from . import debian

__all__ = [ 'list', 'configure']


blueprint = blueprints.get(__name__)

config_dir = '/etc/'
sysctl_dir = os.path.join(config_dir, 'sysctl.d/')
path=os.getcwd()


@task 
@task 
def list(lista=False):
    """
    List sysctl lista for one or more values sysctl.list:lista='vm.swappiness;vm.panic_on_oom'
    """
    with sudo():
        if lista==False:
            run("sysctl -a")
        else :
            lista2=lista.split(';')
            values=[]
            for l in lista2:
                values.append(run("sysctl "+l))
            for value in values: 
                info(value)
@task
def configure():
    """
    Configure sysctl settings
    """
    with sudo():
       
        uploads = []

        # Configure application
        local_params=blueprint.get('params',[])
        uploads.append(blueprint.upload('./sysctl.conf',config_dir,{"params" : local_params}))
        uploads.append(blueprint.upload('./sysctl.d/', sysctl_dir))

        info("In order for the new settings to work you need to reboot the system !!")
