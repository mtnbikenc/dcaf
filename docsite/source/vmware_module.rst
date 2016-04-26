VMware Module
=============

The VMware module is a bare-metal deployment of a VMware virtual infrastructure
and a pre-configured foundation cluster.

The module will do the following:

- Install and configure vSphere 5.5 with VSAN
- Deploy and configure the vCenter Server Appliance
- Create the Virtual Data Center and (VDC) and cluster
- Create and configure the vSphere Distributed Switch (vDS)

At this point there would be a vSPhere 5.5 virtual infrastructure deployed with a
management cluster and networking configured. The management cluster is referred
to as the ``foundation`` cluster as it is intended to be the foundation of the
virtual infrastructure. To use the automation create the CSC DCAF inventory and
variable files then run the playbook(s).

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

Create the Inventory
--------------------

The CSC DCAF inventory is located in the ``/opt/autodeploy/projects/inventory``
folder and is the central inventory for all modules. It is based on the Ansible
inventory hierarchy. The inventory found within the module is only provided as an
example.

Inventory Directory/File Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module follows the default Ansible inventory hierarchy. It only contains the
files necessary for it to run. Notice there are four ``foundation-esxi-xx.yml``
files and a ``foundation-vcsa.yml`` file. When the inventory is created in the
``projects/inventory`` folder these files will be copied and renamed for each host
in the ``hosts.ini`` file per the environment.

.. code-block:: bash

    /vmware/inventory/
    -- /group_vars
          foundation_esxi.yml
       -- /all
             common.yml
             secrets.yml
    -- hosts.ini
    -- /host_vars
          foundation-esxi-01.yml
          foundation-esxi-02.yml
          foundation-esxi-03.yml
          foundation-esxi-04.yml
          foundation-vcsa.yml

hosts.ini
~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The format and contents of
this file will vary depending on the what automation is being used.

.. note::

  The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
  a module or the role the host will have within the module. Each :code:`[group]` name
  should match the corresponding ``inventory/group_vars/group_name.yml`` group variable
  file if it has one. All hosts listed should be under a :code:`[group]` heading.

- **hosts.ini** - Copy the ``/vmware/inventory/host_vars/hosts.ini`` file
  to the ``/opt/autodeploy/projects/inventory/`` folder. Edit it to reflect the
  number of hosts and correct host names for the deployment. This file should
  contain the DNS resolvable names of the hosts being deployed.

The ``/vmware/inventory/hosts.ini`` file contains the following:

.. code-block:: bash

    # ------------------------------------------------------------------
    # Do not modify a [group:children] section, they are module specific
    # ------------------------------------------------------------------

    # This entry should always be present - do not modify
    [autodeploynode]
    localhost ansible_connection=local

    # Global group for module variables, should contain all other groups.
    [vsphere:children]
    esxi
    vcsa

    [esxi:children]
    foundation_esxi

    # Host(s) to be deployed - modify as needed
    [foundation_esxi]
    foundation-esxi-01
    foundation-esxi-02
    foundation-esxi-03
    foundation-esxi-04

    # VCSA to be deployed - modify as needed
    [vcsa]
    foundation-vcsa

.. note::

  Do not modify a group of groups :code:`[group:children]`. These groups are defined
  by the module. Add the required hosts in the respective :code:`[group]` section
  as needed.

Modify Host & Module Variables
------------------------------

This module uses multiple variables that are managed in various files. The
``/opt/autodeploy/projects/inventory/host_vars/`` folder contains host specific
variable files and the ``/opt/autodeploy/projects/inventory/group_vars/`` folder
contains module specific variable files.

host_vars
~~~~~~~~~

The variables that will be applied to a specific host are stored in a ``host_name.yml``
file. There are five in the example inventory, one for each ``foundation`` host and
one for the ``VCSA``.

- **host_name.yml** - Copy all of the ``host_name.yml`` files to the ``/projects/inventory/host_vars/`` folder.
  Rename and edit them as needed. There should be one
  file for for each host in the ``hosts.ini`` file. If the deployment has more than
  four foundation hosts copy one of the existing foundation ``host_name.yml`` files,
  rename and edit it as needed.

.. code-block:: bash

    /vmware/inventory/
    -- /host_vars
          foundation-esxi-01.yml
          foundation-esxi-02.yml
          foundation-esxi-03.yml
          foundation-esxi-04.yml
          foundation-vcsa.yml

Below is the example ``foundation-esxi-01.yml``

.. code-block:: yaml

    ---
    # The smbios-uuid is an identifier used for bare metal deployments.
    smbios_uuid: { retrieve for each host using hardware vendor management tools }

    # IPMI and PXE IP address
    ipmi_ip_address: x.x.x.x
    pxe_ip_address: x.x.x.x

    # Host name and IP addresses
    hostname: host_name
    mgmt_ip_address: x.x.x.x
    vmotion_ip_address: x.x.x.x
    vsan_ip_address: x.x.x.x

.. note::

    Each ``host_name.yml`` file for a physical host must include the host hardware
    :code:`smbios-uuid`. This can be found using the hosts vendor management tools.
    Refer to the vendor documentation for more information.

    The ``smbios-uuid`` is unique and specific to the hardware so it must be different
    in each ``host_name.yml`` file.

group_vars
~~~~~~~~~~

As mentioned above Ansible allows you to group hosts and assign variables to a
:code:`[group]`. This allows you to run plays against multiple hosts without
having to specify them individually. The variables that will be applied to a
specific group, or group of groups, are stored in a ``group_name.yml`` file. The
name of this file must match the name of the corresponding :code:`[group]` in the
``hosts.ini`` file.

This module uses a multiple group_vars files found in the ``/vmware/inventory/group_vars/``. Notice that the name of the file here matches the :code:`[group]`
name from the ``hosts.ini`` file. Also notice there is an ``all`` folder here as
well. Any ``.yml`` file in the ``all`` folder is available to all hosts.

- **foundation-esxi.yml** - Copy the ``/vmware/inventory/group_vars/foundation-esxi.yml`` file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder
  and modify as needed per the environment.

Below is the example ``foundation-esxi.yml`` file. Review all variables and change
as needed.

.. code-block:: yaml

    ---
    # -----------------------------------------------------------------------
    # Do not modify a "{{ variable }}" in this file, find where it is defined
    # and change there if needed.
    # -----------------------------------------------------------------------

    # Ansible system variables
    ansible_ssh_user: root
    ansible_ssh_pass: "{{ site_passwd }}"

    # VLAN IDs for module
    mgmt_vlan_id: 1801
    vmotion_vlan_id: 1802
    vsan_vlan_id: 1803

    # Vendor management utility credentials
    ipmi_username:
    ipmi_password:

- **/group_vars/all/** ``.yml`` files - Copy the ``/all`` folder and its contents
  to the ``/opt/autodeploy/projects/inventory/group_vars`` folder. Review all variables
  and change as needed.

Below is the example ``/group_vars/all/common.yml`` file. Review all variables and change as needed.

.. code-block:: yaml

    ---
    # These are deployment IP addresses
    autodeploynode: x.x.x.x
    domain_name: your_domain
    dns_servers: 192.168.70.3,192.168.70.4
    dns_server: 192.168.70.3
    ntp_servers: 172.17.16.10
    pxe_subnet_mask: 255.255.255.0

    # Module variables used by Hanlon
    hanlon_base_url: http://{{ auto_deploy_node }}:8026/hanlon/api/v1/
    esxi_iso_path: /home/hanlon/image/VMware-VMvisor-Installer-201501001-2403361.x86_64.iso
    esxi_image_name: VMware_ESXi
    esxi_version: 5.5

    # ESXi license must be valid or deployment will fail
    # esx_license was moved into all/secrets.yml (expires 9/14/2015)
    # esx_license:
    esxi_username: root
    mgmt_vdc: Test-Lab
    mgmt_cluster: Foundation
    mgmt_vmk: vmk1
    mgmt_subnet_mask: 255.255.255.0
    vmotion_vmk: vmk2
    vmotion_subnet_mask: 255.255.255.0
    vsan_vmk: vmk3
    vsan_subnet_mask: 255.255.255.0
    dvs_vmnic: vmnic5
    vss_vmnic: vmnic4

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the ``/roles/some_role/defaults`` and ``/roles/some_role/vars`` folders. Typically only the ``/roles/some_roles/defaults`` would need to be modified. Always review both sets of variables for content.

.. code-block:: bash

    /bare-metal-os/roles/some_role
    -- /defaults
          main.yml
    -- /vars
          main.yml

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

At this point the vSphere virtual infrastructure and foundation cluster have been
installed and configured on all hosts listed in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
