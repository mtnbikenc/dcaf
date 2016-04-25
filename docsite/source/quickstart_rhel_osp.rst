RHEL-OSP Quick Start Guide
==========================

This Quick Start Guide describes how to use CSC DCAF Automation to deploy the Red
Hat OpenStack Platform with high availability on base RHEL installations. It uses
the following resources:

- `RHEL-OSP <https://github.com/csc/dcaf/rhel-osp>`_ - An automated deployment of
  a Red Hat OpenStack Cluster with high availability.

The RHEL-OSP project is intended to be utilized on a CSC DCAF bare-metal deployment.

Before You Begin
----------------

Ensure that the following requirements are met:

Internal virtual IPs

haproxy_vip

Run the RHEL-OSP Automation
---------------------------

To use the RHEL-OSP automation modify the inventory and variables then run the
playbook(s).

Modify the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the bare-metal-os module but must be modified to use with RHEL-OSP. For more
information and examples of this file refer to the CSC DCAF project documentation.

Edit the inventory to reflect your environment.

- **hosts.ini** - Modify the ``opt/autodeploy/projects/inventory/hosts.ini`` and
  add the required :code:`[group]` sections and desired hosts. Use the
  ``opt/autodeploy/projects/dcaf/rhel-osp/inventory/hosts.ini`` as a template and
  change values as needed.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    RHOSP roles. Each :code:`[group]` heading will contain a host or a child
    ``group`` of hosts. If editing this file append to it and ensure there is no
    duplication. All hosts listed should be under a :code:`[group]` heading.

.. code-block:: yaml

    Example:
    # Host(s) with the Controller role
    [controller]
    controller1
    ...

    # Host(s) with the Compute role
    [compute]
    compute1
    ...

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses multiple variables that are managed in various files. The
``host_vars/host_name.yml`` file contains host specific variables and the
``group_vars/group_name.yml`` files contain project specific variables.

.. note::

    The RHEL-OSP module has multiple types of `hosts` based on the RHOSP role or
    service. Copy, rename and modify the appropriate type of example host file as
    needed.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host, based on RHOSP role or service, in the hosts.ini file. Create or
  modify these files by copying the contents of the appropriate ``/opt/autodeploy/projects/dcaf/rhel-osp/inventory/host_vars/example_host.yml``
  and changing values as needed.

.. note::

    The RHEL-OSP module has multiple `group_name` variable files based on the RHOSP
    role or service.

- **group_name.yml** - Copy all of the ``/opt/autodeploy/projects/dcaf/rhel-osp/inventory/group_vars/group_name.yml``
  files to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Deploy the Red Hat OpenStack Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next run the ``rhel-osp/site.yml`` playbook to deploy RHEL OSP to the hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/rhel-osp
    ansible-playbook site.yml -i ../../inventory/hosts.ini

At this point RHEL OSP has been installed and configured on all hosts listed
in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
