Bare-Metal-OS Module
====================

The Bare-Metal-OS module is the foundation for much of the CSC DCAF automation. It
deploys the base Operating System for other modules and projects to use. It currently
supports Red Hat Enterprise Linux.

At this point the Autodeploynode has been successfully created and is ready to
use. To use the Bare-Metal-OS automation create the CSC DCAF inventory and variable
files then run the playbook(s).

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

Create the Inventory
--------------------

The CSC DCAF inventory is located in the ``/opt/autodeploy/projects/inventory``
folder and is the central inventory for all modules. It is based on the Ansible
inventory hierarchy. The inventory found within the module is only provided as an
example.

Inventory Directory/File Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module follows the default Ansible inventory hierarchy. It only contains the
files necessary for it to run. Notice there is only one ``hostname-1.yml`` file.
When the inventory is created in the ``projects/inventory`` folder the ``hostname-1.yml``
file will be copied and renamed for each host in the ``hosts.ini`` file. The
``autodeploynode.yml`` is a project default and will need to be copied when the
inventory is created.

.. code-block:: bash

    /bare-metal-os/inventory/
    -- /group_vars
          bare_metal_os.yml
    -- hosts.ini
    -- /host_vars
          autodeploynode.yml
          hostname-1.yml

hosts.ini
~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The format and contents of
this file will vary depending on the what automation is being used.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    a module or the role the host will have within the module. Each :code:`[group]` name
    should match the corresponding ``inventory/group_vars/group_name.yml`` group variable
    file if it has one. All hosts listed should be under a :code:`[group]` heading.

- **hosts.ini** - Copy the ``/opt/autodeploy/projects/dcaf/modules/bare-metal-os/inventory/host_vars/host.ini`` file to the ``/opt/autodeploy/projects/inventory/`` folder. Edit it to
  reflect the number of hosts and correct host names for the  deployment. This file
  should contain the DNS resolvable names of the hosts being deployed.

The ``bare-metal-os/inventory/hosts.ini`` file contains the following:

.. code-block:: bash

    # ------------------------------------------------------------------
    # Do not modify a [group:children] section, they are module specific
    # ------------------------------------------------------------------

    # This entry should always be present - do not modify
    [autodeploynode]
    localhost ansible_connection=local

    # Global group for module variables, should contain all other groups.
    [bare_metal_os]
    autodeploynode
    deploy

    # Host(s) to be deployed - modified as needed
    [deploy]
    hostname-1
    ...

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
file. There are two in the example inventory, one for the ``autodeploynode`` and
one for ``hostname-1``.

- **host_name.yml** - Copy both the ``autodeploynode`` and ``hostname-1`` files
  to the ``/projects/inventory/host_vars/`` folder. From there copy, rename and
  edit the ``hostname-1.yml`` file for each host in the ``hosts.ini`` file.

.. code-block:: bash

    /bare-metal-os/inventory/
    -- /host_vars
          autodeploynode.yml
          hostname-1.yml

Below is the example ``host_name.yml``

.. code-block:: yaml

    ---
    # The ip and pxe ip address of the host
    ansible_ssh_host: x.x.x.x
    pxe_ip_address: x.x.x.x

    # The smbios-uuid is an identifier used for bare metal deployments.
    smbios_uuid: { retrieve for each host using hardware vendor management tools }

.. note::

    Each ``host_name.yml`` file must include the host hardware :code:`smbios-uuid`.
    This can be found using the hosts vendor management tools. Refer to the vendor
    documentation for more information.

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

This module uses a single group_vars file ``/bare-metal-os/inventory/group_vars/bare_metal_os.yml``.
Notice it matches the group of groups for the module so all hosts will have access
to these variables.

- **bare_metal_os.yml** - Copy the ``/bare-metal-os/inventory/group_vars/bare_metal_os.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Below is the example ``group_name.yml`` file. Edit as needed for your environment.
Review all the variables but it is recommended to only change the following.

.. code-block:: yaml

    ---
    # if the hosts have additional disks that need to be pratitioned
    partition_additional_disks: false

    # IP address of the autodeploynode
    autodeploynode: x.x.x.x

    # DNS IP address
    dns1: x.x.x.x

    # Root password for host(s)
    site_password: localpassword

    # Hardware vendor management user/password
    ipmi_username: root
    ipmi_password: localpassword

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the ``/roles/some_role/defaults``
and ``/roles/some_role/vars`` folders. Typically only the ``/roles/some_roles/defaults``
would need to be modified. Always review both sets of variables for comtent.

.. code-block:: bash

    /bare-metal-os/roles/some_role
    -- /defaults
          main.yml
    -- /vars
          main.yml

Run Bare-Metal-OS Automation
----------------------------

Now that the inventory has been created the Bare-Metal-OS automation can be used.

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
