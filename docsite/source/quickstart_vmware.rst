VMware Module Quick Start Guide
===============================

This Quick Start Guide describes how to use CSC DCAF Automation to deploy a VMware
virtual infrastructure to bare-metal hardware. It uses the following resources:

- `VMware <https://github.com/csc/dcaf/vmware>`_ - An automated deployment of
  a VMware Virtual Infrastructure on bare-metal hardware.

- `Hanlon <https://github.com/csc/Hanlon>`_ - As an advanced provisioning
  platform which can provision both bare-metal and virtual systems.

Before You Begin
----------------

Ensure that the following requirements are met:

- A user account on the VMware website to download the software.
- Download the vSphere 5.5 ISO and VCSA .ova to ``/opt/autodeploy/resources/ISO``
  folder.
- OVF Tool installed on the Autodeploynode
- vSphere CLI installed on the Autodeploynode

Physical Hardware
~~~~~~~~~~~~~~~~~

DCAF was developed and tested with the following hardware:

- DELL PowerEdge 630 | PowerEdge 730
- DELL PERC H730 RAID Controller

The physical hardware being deployed to meet the following:

- The physical hardware has been installed and connected to the network
- Hosts to be deployed to have pass-through RAID controllers
- The system BIOS has been pre-configured, e.g. VT is enabled, boot order
- The out-of-band management IP addresses have been set and IPMI access enabled

Network Requirements
~~~~~~~~~~~~~~~~~~~~

There are several network requirements for the deployment.

- DNS server IP addresses need to be provided
- NTP server IP address needs to be provided
- The following VLANS are required:
    - Out-of-band management (IPMI)
    - PXE Network
    - Management
    - vMotion
    - VSAN

- VMKernel IP addresses for each ESXi host
    - vmk0 : PXE Network
    - vmk1 : Management Network
    - vmk2 : vMotion Network
    - vmk3 : VSAN Network

- Out-of-band Network IP address for each host
- Management IP address for each host and VCSA
- 2 10GbE connections to the 10GbE network switches
- The upstream and management networks are pre-configured

Run the VMware Automation
-------------------------

To use the VMware automation create the inventory and variables then run the
playbook(s).

Create the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the :code:`hosts.ini` file. The format and contents of
this file will vary depending on the what automation is being used. For more information
and examples of this file refer to the CSC DCAF project documentation.

Edit the inventory to reflect your environment.

- **hosts.ini** - Copy the ``/vmware/inventory/host_vars/hosts.ini`` file
  to the ``/opt/autodeploy/projects/inventory/`` folder. Edit it to reflect the
  number of hosts and correct host names for the deployment. This file should
  contain the DNS resolvable names of the hosts being deployed.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    a module or the role the host will have within the module. Each :code:`[group]` name
    should match the corresponding ``inventory/group_vars/group_name.yml`` group variable
    file if it has one. All hosts listed should be under a :code:`[group]` heading.

.. code-block:: yaml

    Example snippet from the hosts.ini file:
    # Host(s) to be deployed - modify as needed
    [foundation_esxi]
    foundation-esxi-01
    foundation-esxi-02
    ...

    # VCSA to be deployed - modify as needed
    [vcsa]
    foundation-vcsa

.. note::

    Do not modify a group of groups :code:`[group:children]`. These groups are defined
    by the module. Add the required hosts in the respective :code:`[group]` section
    as needed.

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses multiple variables that are managed in various files. The
``host_vars/host_name.yml`` file contains host specific variables and the
``group_vars/group_name.yml`` files contain project specific variables.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  file for each host, based on VMware role or service, in the hosts.ini file. Copy
  them from the ``/vmware/inventory/host_vars`` folder to the ``/opt/autodeploy/projects/inventory/host_vars``
  folder and modify as needed.

.. note::

    Each ``host_name.yml`` file must include the host hardware :code:`smbios-uuid`.
    This can be found using the hosts vendor management tools. Refer to the vendor
    documentation for more information.

- **foundation-esxi.yml** - Copy the ``/vmware/inventory/group_vars/foundation-esxi.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

- **/group_vars/all/** ``.yml`` files - Copy the ``/vmware/inventory/group_vars/all``
  folder and its contents to the ``/opt/autodeploy/projects/inventory/group_vars``
  folder. Review all variables and change as needed.

Run VMware Automation
---------------------

Now that the inventory has been created the VMware automation can be used.

Prepare Hosts for Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order for Hanlon to deploy anything to a host the host has to be `discovered`
by Hanlon. The discovery process provides Hanlon information about the host.

To have the hosts `discovered` by Hanlon simply boot each host. The host will PXE
boot to Hanlon, register itself and power off.

Deploy VMware Virtual Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next run the ``/vmware/site_deploy.yml`` playbook to deploy the vSphere to the
hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/modules/vmware
    ansible-playbook site_deploy.yml -i ../../inventory/hosts.ini

At this point the VMware virtual infrastructure and foundation cluster have been
installed and configured on all hosts listed in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
