Slimer Quick Start Guide
========================

This Quick Start Guide describes how to use CSC DCAF Automation to deploy the Red
Hat OpenStack Platform with high availability on base RHEL installations. It uses
the following resources:

- `Slimer <https://github.com/csc/slimer>`_ - The CSC Slimer project, a fork of
  `abrezhnev/slimer <https://github.com/abrezhnev/slimer>`_, is used to deploy
  the Red Hat OpenStack Platform with high availability on base RHEL installations.

The Slimer project is intended to be utilized on a CSC DCAF bare-metal OS deployment.

Before You Begin
----------------

Ensure that the following requirements are met:

Internal virtual IPs

- ceilometer_vip
- cinder_vip
- glance_vip
- heat_vip
- horizon_vip
- keystone_vip
- lb_db_vip
- neutron_vip
- nova_vip
- rabbit_vip
- scaleio_vip
- swift_vip

Public virtual IPs

- vip_ceilometer_pub
- vip_cinder_pub
- vip_glance_pub
- vip_heat_pub
- vip_horizon_pub
- vip_keystone_pub
- vip_neutron_pub
- vip_nova_pub

Horizon

- horizon_internal_servername
- horizon_public_servername

Run the Slimer Automation
-------------------------

To use the Slimer automation modify the inventory and variables then run the playbook(s).

Modify the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the bare-metal-os module but must be modified to use with Slimer. For more information
and examples of this file refer to the CSC DCAF project documentation.

The inventory was created by the bare-metal-os module but must be modified to use
with Slimer.

Edit the inventory to reflect your environment.

- **hosts.ini** - Modify the ``/opt/autodeploy/projects/inventory/hosts.ini`` and
  group the hosts by role. Use the ``/opt/autodeploy/projects/slimer/inventory/hosts.ini``
  as a template and change values as needed. This file should contain the DNS
  resolvable names of the hosts being deployed to.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    a module or the role the host will have within the module. Each :code:`[group]`
    name should match the corresponding ``inventory/group_vars/group_name.yml`` group
    variable file. If editing this file append to it and ensure there is no duplication.
    All hosts listed should be under a :code:`group` heading.

.. code-block:: yaml

    # Host(s) with the Controller role
    [controller]
    controller-1
    ...

    # Host(s) with the Compute role
    [compute]
    compute-1
    ...

.. note::

    Do not modify a group of groups :code:`[group:children]`. These groups are defined
    by the module. Add the required hosts in the respective :code:`[group]` section
    as needed.

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses multiple variables that are managed in various files. The
``host_vars/host_name.yml`` file contains host specific variables and the ``group_vars/all.yml``
file contains project specific variables.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/slimer/inventory/host_vars/host_name.yml``
  for each host in the hosts.ini file. Modify these files by copying the contents of
  the ``/opt/autodeploy/projects/slimer/inventory/host_vars/example_host.yml`` and
  modifying as needed.

- **all.yml** - Copy the ``/opt/autodeploy/projects/slimer/inventory/group_vars/all.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder, rename it
  ``slimer.yml`` and modify as needed per the environment.

Deploy the Red Hat OpenStack Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next run the ``slimer/site.yml`` playbook to deploy RHEL OSP to the hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/slimer
    ansible-playbook site.yml -i ../inventory/hosts.ini

At this point RHEL OSP has been installed and configured on all hosts listed in the
``/opt/autodeploy/projects/inventory/hosts.ini``.
