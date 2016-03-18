Bare Metal OS Deployment
========================

At this point the AutoDeployNode has been successfully created and is ready to
use. The automation projects source configuration needs to be sanitized and
configured for the deployment environment.

Create an inventory
-------------------

Begin by editing the example inventory file :code:`inventory/example_inventory.csv`
with details reflecting the deployment environment. The example\_inventory.csv has
some added columns that this deployment won’t be used that should be removed
including disk, fstype, mount\_opts and mount. An inventory creation playbook
:code:`site_inventory.yml` will be run which will use this file to create all
needed host variables.

Update group variables
~~~~~~~~~~~~~~~~~~~~~~

There is a file which defines variables for the project used deployment-wide
:code:`inventory/group_vars/all.yml`. This needs to be edited with values that
reflect the deployment environment in order for the following scripts to function.

Running the initial deployment playbook
---------------------------------------

After all variables are put in place, the inventory playbook needs to be run:

.. code-block:: bash

    ansible-playbook site_inventory.yml

This first run will populate all needed host variables and definitions from the
inventory file previously created. This playbook will need to be run a second
time to retrieve the SMBIOS UUID from each host and update the host\_vars files:

.. code-block:: bash

    ansible-playbook site_inventory.yml

Resetting the environment and preparing for deployment
------------------------------------------------------

The next playbook being run will power cycle all nodes in the deployment and
ensure they have been discovered:

.. code-block:: bash

    ansible-playbook site_reset.yml


Configuration Reference
-----------------------

Directory/File Structure
~~~~~~~~~~~~~~~~~~~~~~~~

The Ansible configurations are stored in :code:`YAML` format. They contain all the
information needed by the Ansible Playbooks and are stored in .yml format. Refer
to http://docs.ansible.com/YAMLSyntax.html for more information about the
``Ansible YAML Syntax``.

Ansible works against multiple systems in the infrastructure at the same time. It
does this by selecting portions of systems listed in the Ansible :code:`inventory`
file. This inventory is configurable and multiple inventory files can be used at
the same time. Refer to http://docs.ansible.com/intro_inventory.html for more
information about the Ansible inventory.

This is how the inventory for Bare-Metal-OS is structured. Variables for Slimer
and Ansible-ScaleIO are also included in this inventory. Notice there is a
:code:`host_var` file for each host.

.. code-block:: bash

    inventory/
    ├── group_vars
    │   ├── all.yml
    ├── hosts.ini
    ├── host_vars
    │   ├── autodeploynode.yml
    │   ├── compute1.yml
    │   ├── compute2.yml
    │   ├── compute3.yml
    │   ├── compute4.yml
    │   ├── controller1.yml
    │   ├── controller2.yml
    │   ├── controller3.yml
    │   ├── scaleio-1.yml
    │   ├── scaleio-2.yml
    │   ├── scaleio-3.yml
    │   ├── swift1.yml
    │   ├── swift2.yml
    │   └── swift3.yml


hosts.ini
~~~~~~~~~

The hosts.ini file should include all hosts in the environment to be deployed to.
The hosts can be grouped as needed by specifying the :code:`[group name]` in
square brackets. Refer to http://docs.ansible.com/intro_inventory.html for more
information about the Ansible inventory.

This inventory supports Slimer and Ansible-ScaleIO so in our example there are
groups for both. There is a :code:`[group_heading]` for each group of like hosts
with the corresponding hosts beneath it. Specifically for bare-metal-os,
the :code:`[deploy:children]` group is used.

.. code-block:: bash

    [controller]
    controller-1
    controller-2
    controller-3

    [swift]
    controller-1
    controller-2
    controller-3

    [compute]
    compute-1
    compute-2
    compute-3
    compute-4

    [scaleio]
    compute-1
    compute-2
    compute-3
    compute-4
    scaleio-1
    scaleio-2
    scaleio-3

    [mdm]
    scaleio-1
    scaleio-2

    [tb]
    scaleio-3

    [auto_deploy_node]
    auto-deploy-node

    [mongodb:children]
    controller

    [openstack:children]
    controller
    compute
    swift

    [deploy:children]
    openstack
    scaleio

    [sds:children]
    mdm
    tb

    [gateway:children]
    controller

    [sdc:children]
    sds
    gateway
    compute

.. note::

    The :code:`[mdm]` and :code:`[tb]` sections should refer to the same hosts
    as the :code:`[compute]` section if you are co-locating the ScaleIO and
    Compute services.

host_vars
~~~~~~~~~

The variables that will be applied to a specific host by Ansible are stored in
a :code:`inventory/host_vars/host_name.yml` files. There should be one of these
for each host in the hosts.ini file. These files should be created automatically
when :code:`site_inventory.yml` is run in the previous steps.

.. code-block:: bash

    ├── host_vars
    │   ├── autodeploynode.yml
    │   ├── compute1.yml
    │   ├── compute2.yml
    │   ├── compute3.yml
    │   ├── compute4.yml
    │   ├── controller1.yml
    │   ├── controller2.yml
    │   ├── controller3.yml
    │   ├── scaleio-1.yml
    │   ├── scaleio-2.yml
    │   ├── scaleio-3.yml
    │   ├── swift1.yml
    │   ├── swift2.yml
    │   └── swift3.yml


group_vars
~~~~~~~~~~

As mentioned above Ansible allows you to group hosts and assign variables to a
:code:`[group]`. This allows you to run plays against multiple hosts without
having to specify them individually. The group \_vars variables are in the
:code:`inventory/group_vars/all.yml`. The all.yml is used by all hosts in the
hosts.ini.

Edit the :code:`group_vars/all.yml` file as needed for your environment. The
following variables are all you may need to change.


.. code-block:: yaml

    ---
    partition_additional_disks: false
    auto_deploy_node: x.x.x.x
    dns1: x.x.x.x
    inventory_path: ./inventory/
    inventory_csv_file: ./inventory/example_inventory.csv
    site_password: localpassword
    ipmi_username: root
    ipmi_password: localpassword

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the role/vars
directory.
