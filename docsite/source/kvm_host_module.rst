KVM-Host Module
===============

The KVM-Host module is intended to be utilized on a CSC DCAF bare-metal RHEL
deployment but can be used on an existing environment providing it meets module
requirements. The module will add KVM host support to specified RHEL hosts then
deploy and configure virtual machines on them. The number of KVM hosts and VMs
to be deployed is dictated by the inventory.

The KVM-Host deployment contains two types of hosts, one is the physical host (kvm-host)
the other is a virtual host (vm). They are differentiated by the inventory.

At this point the RHEL OS has been successfully deployed on all hosts in the ``hosts.ini``
file by the Bare-Metal-OS module. To use the KVM-Host automation modify the CSC
DCAF inventory and variable files then run the playbook(s).

Before You Begin
----------------

Ensure that the following requirements are met:

Two Host Types
--------------

The modules has two host types differentiated by the inventory:

- **kvm-host** is a pre-installed RHEL host that this module will install and configure
  KVM host support on.

- **vm** hosts are just that, virtual machines created for the Red Hat OpenStack
  Platform. The number of VMs created depends on how the deployment is architected
  configured by the inventory.

Modify the Inventory
--------------------

The CSC DCAF inventory is located in the ``/opt/autodeploy/projects/inventory``
folder and is the central inventory for all modules. It is based on the Ansible
inventory hierarchy. The inventory found within this module is only provided as an
example.

Inventory Directory/File Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module follows the default Ansible inventory hierarchy. It only contains the
files necessary for it to run. Notice there is an ``example-host-type.yml`` file
for each of the two host types.

.. code-block:: bash

    /kvm-host/inventory/
    -- /group_vars
          kvm_host.yml
    -- hosts.ini
    -- /host_vars
          example_kvmhost.yml
          example_vm.yml

hosts.ini
~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the Bare-Metal-OS module but must be modified to use with KVM-Host.

Edit the inventory to reflect your environment.

- **hosts.ini** - Copy and append the contents of the ``/kvm-hosts/inventory/hosts.ini``
  file to the ``/opt/autodeploy/projects/inventory/hosts.ini`` file and modify as needed.
  If appending to this file ensure there is no duplication. All hosts listed should be
  under a :code:`[group]` heading.

.. note::

    The ``kvm-host/inventory/hosts.ini`` file contains many :code:`[group]` sections
    with hosts and :code:`[group:children]` sections with groups as an example. Only
    modify the :code:`[group]` of hosts as needed.

.. code-block:: yaml

    Example:
    # ------------------------------------------------------------------
    # Do not modify a [group:children] section, they are module specific
    # ------------------------------------------------------------------

    # This entry should always be present - do not mpdify
    [autodeploynode]
    localhost ansible_connection=local

    # KVM host machine(s) - modify as needed
    [kvmhosts]
    kvm-controller-1
    kvm-controller-2
    kvm-controller-3

    # VM(s) to be created - modify as needed
    [nodes]
    controller-1
    controller-2
    controller-3
    haproxy-1
    haproxy-2
    network-1
    network-2
    network-3
    swift-1
    swift-2
    swift-3

.. note::

    Do not modify a group of groups :code:`[group:children]`. These groups are defined
    by the module. Add the required hosts in the respective :code:`[group]` section
    as needed.

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module uses multiple variables that are managed in various files. The
``/kvm-host/inventory/host_vars/`` folder contains host specific
variable files and the ``/kvm-host/inventory/group_vars/`` folder
contains module specific variable files.

host_vars
~~~~~~~~~

The variables that will be applied to a specific host are stored in a ``host_name.yml``
file. There are two in the example inventory, one for the ``autodeploynode`` and
one for ``hostname-1``.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host, physical and virtual, in the hosts.ini file. Since these files
  were created by a previous module they may need to be renamed. For example if
  the files are named ``host_name-1, host_name-2, ...`` they may will need to be
  renamed for your deployment ``kvm-controller-1,kvm-controller-2, ...``. Copy and
  append the contents of the appropriate ``/kvm-host/inventory/host_vars/example_kvmhost.yml``
  or ``/kvm-host/inventory/host_vars/example_vm.yml`` file and changing values as needed.

.. code-block:: bash

    /kvm-host/inventory/
    -- /host_vars
          example_kvmhost.yml
          example_vm.yml

.. note::

    The KVM-Host module has two types of `hosts`, one is the physical host (kvm-host)
    and the virtual host (vm). Copy, rename and modify the appropriate type of example
    host file as needed.

Below is the ``example_kvmhost.yml``

.. code-block:: yaml

    ---
    ansible_ssh_host: 172.17.16.70
    mgmt_nic: em3

    vlan_interface:
      ext_if:
        bond: "bond0"
        dns1: 192.168.70.3
        gateway: 172.17.21.1
        ipaddr: 172.17.21.70
        netmask: 255.255.255.0
        vlan: '{{ external_vlan }}'
      int_if:
        bond: "bond0"
        dns1: 172.17.10.22
        gateway: 172.17.17.1
        ipaddr: 172.17.17.70
        netmask: 255.255.255.0
        vlan: '{{ management_vlan }}'
      storage_if:
        bond: "bond0"
        ipaddr: 172.17.19.70
        netmask: 255.255.255.0
        vlan: '{{ storage_public_vlan }}'
      vm_ext_if:
        bond: "bond0"
        ipaddr: 172.17.20.70
        netmask: 255.255.255.0
        vlan: '{{ storage_cluster_vlan }}'
      tun_if:
        bond: "bond0"
        ipaddr: 172.17.18.70
        netmask: 255.255.255.0
        vlan: '{{ tenant_vlan }}'

group_vars
~~~~~~~~~~

As mentioned above Ansible allows you to group hosts and assign variables to a
:code:`[group]`. This allows you to run plays against multiple hosts without
having to specify them individually. The variables that will be applied to a
specific group, or group of groups, are stored in a ``group_name.yml`` file. The
name of this file must match the name of the corresponding :code:`[group]` in the
``hosts.ini`` file.

This module uses a single group_vars file ``/kvm-host/inventory/group_vars/kvm_host.yml``.
Notice it matches the :code:`[kvm_host]` group section in the ``hosts.ini`` for the
module so all hosts will have access to these variables.

.. code-block:: yaml

    /kvm-host/inventory/
    -- /group_vars
          kvm_host.yml

- **kvm_host.yml** - Copy the ``/kvm-host/inventory/group_vars/kvm_host.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the ``/roles/some_role/defaults``
and ``/roles/some_role/vars`` folders. Typically only the ``/roles/some_roles/defaults``
would need to be modified. Always review both sets of variables for comtent.

.. code-block:: none

    /kvm-host/roles/some_role
    -- /defaults
          main.yml
    -- /vars
          main.yml

Deploy the KVM hosts and VMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next run the ``kvm-host/site.yml`` playbook to deploy KVM hosts and the VMs defined
in the inventory ``hosts.ini``:

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/kvm-host
    ansible-playbook site.yml -i ../../inventory/hosts.ini

At this point the KVM host support has been installed and configured on all hosts
and the VMs listed in the ``/opt/autodeploy/projects/inventory/hosts.ini`` have
been created.
