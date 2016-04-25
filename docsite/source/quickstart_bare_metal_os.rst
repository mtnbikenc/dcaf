Bare-metal-OS Quick Start Guide
===============================

This Quick Start Guide describes how to use CSC DCAF Automation to provision an
OS on bare-metal hardware, currently Red Hat Enterprise Linux. It uses the following
resources:

- `dcaf/bare-metal-os <https://github.com/csc/dcaf/bare-metal-os>`_ - An
  automated deployment of an operating system to bare-metal hardware using Hanlon,
  currently the Red Hat Enterprise Linux OS.

- `Hanlon <https://github.com/csc/Hanlon>`_ - As an advanced provisioning
  platform which can provision both bare-metal and virtual systems.

Before You Begin
----------------

Ensure that the following requirements are met:

Physical Hardware
~~~~~~~~~~~~~~~~~

DCAF was developed and tested with the following hardware:

- DELL PowerEdge 630 | PowerEdge 730
- DELL PERC H730 RAID Controller

The physical hardware being deployed to meet the following:

- The physical hardware has been installed and connected to the network
- A 1GB connection for OOB management on the management switch
- 2 10GbE connections to the 10GbE network switches
- The upstream and management network are pre-configured
- The out-of-band management IP addresses are pre-configured
- IPMI is enabled on each host

Network Requirements
~~~~~~~~~~~~~~~~~~~~

There are several network requirements for the deployment.

- DNS server IP addresses need to be provided
- NTP server IP address needs to be provided
- The following VLANS are required:

  - Out-of-band management (IPMI)
  - PXE Network

- Out-of-band Network IP address for each node
- Management IP address for each node

Run Bare-metal-OS Automation
----------------------------

To use the Bare-Metal-OS automation create the inventory and variable files then
run the playbook(s).

Create the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the `hosts.ini`` file. The format and contents of this
file will vary depending on the what automation is being used. For more information
and examples of this file refer to the CSC DCAF project documentation.

- **hosts.ini** - Create the ``/opt/autodeploy/projects/inventory/hosts.ini`` file
  by copying the ``opt/autodeploy/projects/dcaf/modules/bare-metal-os/inventory/host_vars/hosts.ini``,
  and modify as needed. This file should contain the DNS resolvable names of the
  hosts being deployed to.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    a module or the role the host will have within the module. Each :code:`[group]` name
    should match the corresponding ``inventory/group_vars/group_name.yml`` group variable
    file. If editing this file append to it and ensure there is no duplication. All
    hosts listed should be under a :code:`group` heading.

.. code-block:: yaml

    # This entry should always be present
    [autodeploynode]
    localhost ansible_connection=local

    # Host(s) to be deployed
    [deploy]
    hostname1
    hostname2
    ...

Modify Host & Module Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module uses multiple variables that are managed in various files. The
``inventory/host_vars/host_name.yml`` file contains host specific variables and the
``inventory/group_vars/bare_metal_os.yml`` file contains module specific variables.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host in the hosts.ini file. Create these files by copying the
  ``opt/autodeploy/projects/dcaf/modules/bare-metal-os/inventory/host_vars/example_host.ini``,
  rename it to it host_name.yml and modify as needed.

.. note::

    Each ``host_name.yml`` file must include the host hardware :code:`smbios-uuid`.
    This can be found using the hosts vendor management tools. Refer to the vendor
    documentation for more information.

- **bare_metal_os.yml** - Copy the ``/opt/autodeploy/projects/dcaf/modules/bare-metal-os/inventory/group_vars/bare_metal_os.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Prepare Hosts for Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the ``bare-metal-os/site_reset.yml`` playbook to power cycle the hosts and have
them discovered by Hanlon: ​

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/modules/bare-metal-os
    ansible-playbook site_reset.yml -i ../../inventory/hosts.ini

Deploy the OS
~~~~~~~~~~~~~

Next run the ``bare-metal-os/site_deploy.yml`` playbook to deploy the RHEL OS to
the hosts in inventory:

.. code-block:: bash

    ansible-playbook site_deploy.yml -i ../../inventory/hosts.ini

At this point the RHEL OS has been installed and configured on all hosts listed
in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
