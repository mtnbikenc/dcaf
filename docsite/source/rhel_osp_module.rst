RHEL-OSP Module
===============

The RHEL-OSP module uses Keepalived and HAProxy to provide a highly available (HA)
OpenStack cluster. It is intended to be utilized on a CSC DCAF bare-metal RHEL deployment
but can be used on an existing environment providing it meets module requirements.

The RHOSP deployment is complex with numerous services and agents but can be simplified
by grouping the nodes into five different types.

At this point the RHEL OS has been successfully deployed on all hosts in the ``hosts.ini``
file by the Bare-Metal-OS module. To use the RHEL-OSP automation modify the CSC
DCAF inventory and variable files then run the playbook(s).

Before You Begin
----------------

Ensure that the following requirements are met:

- Ansible 2.0
- Heat 2014.2 (required for testing playbooks)
- Internal Virtual IPs

  haproxy_vip

Five Node Types
---------------

The module treats each host as one of five types defined in the inventory.

- **HAProxy** nodes that can be physical or virtual machines that run Keepalived
  and HAProxy providing the virtual IP for the cluster.

- **Controller** nodes that can be physical or virtual machines that run all the
  APIs and support services for the cluster.

- **Network** nodes that can be physical or virtual machines that run the Neutron
  agentsseparate from the control plane.

- **Compute** nodes that are recommended be physical machines to leverage hardware
  acceleration for hosting VMs under KVM.

- **Swift** storage nodes that can be physical or virtual machines that run the
  Swift storage services.

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
for each of the five node types.

.. code-block:: bash

    /rhel-osp/inventory/
    -- /group_vars
          ceilometer.yml
          cinder.yml
          haproxy.yml
          neutron.yml
          openstack.yml
          swift.yml
    -- hosts.ini
    -- /host_vars
          example-compute-host.yml
          example-controller.yml
          example-haproxy.yml
          example-network-node.yml
          example-swift-storage.yml

hosts.ini
~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the Bare-Metal-OS module but must be modified to use with RHEL-OSP.

Edit the inventory to reflect your environment.

- **hosts.ini** - Copy and append the contents of the ``/rhel-osp/inventory/hosts.ini``
  file to the ``/opt/autodeploy/projects/inventory/hosts.ini`` file and modify as
  needed. If appending to this file ensure there is no duplication. All hosts listed
  should be under a :code:`[group]` heading.

.. note::

    The ``rhel-osp/inventory/hosts.ini`` file contains many :code:`[group]` sections
    with hosts and :code:`[group:children]` sections with groups as an example. Only
    modify the :code:`[group]` of hosts as needed.

.. code-block:: bash

    # ------------------------------------------------------------------
    # Do not modify a [group:children] section, they are module specific
    # ------------------------------------------------------------------

    # Host(s) with Compute role - modify as needed
    [compute]
    compute-1
    compute-2
    compute-3
    compute-4
    compute-5
    compute-6
    compute-7

    # Host(s) with Controller role - modify as needed
    [controller]
    controller-1
    controller-2
    controller-3

    # Host(s) with HAProxy role - modify as needed
    [haproxy]
    haproxy-1
    haproxy-2

    # Host(s) that get OpenStack deployed
    [openstack:children]
    controller
    compute
    swift
    haproxy
    neutron-network-node
    scaleio

    # Host(s) with Swift role(s)
    [swift:children]
    swift-proxy
    swift-storage

    [swift-proxy:children]
    controller

    # Host(s) with Swift role - modify as needed
    [swift-storage]
    swift-1
    swift-2
    swift-3

    # Host(s) with SQL role
    [sql:children]
    controller

    # Host(s) with Keystone role
    [keystone:children]
    controller

    # Host(s) with RabbitMQ role
    [rabbitmq_cluster:children]
    controller

    # Host(s) with Glance role
    [glance:children]
    controller

    # Host(s) with Cinder role(s)
    [cinder:children]
    cinder-server
    cinder-volume

    [cinder-server:children]
    controller

    [cinder-volume: children]
    compute

    # Host(s) with Controller-Nova role
    [controller-nova:children]
    controller

    # Host(s) with Heat role
    [heat:children]
    controller

    # Host(s) with Ceilometer role(s)
    [ceilometer-control:children]
    controller

    [ceilometer:children]
    ceilometer-control
    compute

    # Host(s) with Horizon role
    [horizon:children]
    controller

    # Host(s) with Neutron role(s)
    [neutron:children]
    neutron-network-node
    neutron-server

    [neutron-network-node:children]
    controller

    [neutron-server:children]
    controller

    # Host(s) with MongoDB role
    [mongodb:children]
    controller

.. note::

    Do not modify a group of groups :code:`[group:children]`. These groups are defined
    by the module. Add the required hosts in the respective :code:`[group]` section
    as needed.


Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module uses multiple variables that are managed in various files. The
``/rhel-osp/inventory/host_vars/`` folder contains host specific
variable files and the ``/rhel-osp/inventory/group_vars/`` folder
contains module specific variable files.

host_vars
~~~~~~~~~

The variables that will be applied to a specific host are stored in a ``host_name.yml``
file. There are two in the example inventory, one for the ``autodeploynode`` and
one for ``hostname-1``.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host in the hosts.ini file. Since these files were created by a previous
  module they may need to be renamed. For example if the files are named ``host_name-1, host_name-2, ...``
  they may will need to be renamed for your deployment ``controller-1,controller-2, ...``.
  Now copy and append the contents of the appropriate ``example_host.yml`` and change
  values as needed.

.. code-block:: bash

    /rhel-osp/inventory/
    -- /host_vars
          example-compute-host.yml
          example-controller.yml
          example-haproxy.yml
          example-network-node.yml
          example-swift-storage.yml

.. note::

    The RHEL-OSP module has numerous types of ``hosts`` based on the RHOSP role or
    service. Copy, rename and modify the appropriate type of example_host.yml file
    as needed.

Below is the ``example-compute-host.yml``

.. code-block:: yaml

    ---
    virt: false
    dns_if: eth1
    nova_virt_type: kvm

    mgmt_if:
      device: eth0
      ipaddr: 192.168.100.51
      netmask: 255.255.255.0
      gateway: 192.168.100.1
      dns1: 8.8.8.8

    control_if:
      device: eth1
      ipaddr: 192.168.101.51
      netmask: 255.255.255.0

    datanet_if:
      device: eth2
      ipaddr: 172.16.23.51
      netmask: 255.255.255.0

    scaleio_if:
      device: eth3
      ipaddr: 172.16.26.51
      netmask: 255.255.255.0

.. note::

    The ``host_name.yml`` file is being appended to. Check it for duplicate variables.

group_vars
~~~~~~~~~~

As mentioned above Ansible allows you to group hosts and assign variables to a
:code:`[group]`. This allows you to run plays against multiple hosts without
having to specify them individually. The variables that will be applied to a
specific group, or group of groups, are stored in a ``group_name.yml`` file. The
name of this file must match the name of the corresponding :code:`[group]` in the
``hosts.ini`` file.

This module uses several group_vars files located in the ``/rhel-osp/inventory/group_vars``
folder. Notice their names match a :code:`[group]` or :code:`[group:children]` so
all hosts in these groups will have access to the respective variables.

.. code-block:: yaml

    /rhel-osp/inventory/
    -- /group_vars
          ceilometer.yml
          cinder.yml
          haproxy.yml
          neutron.yml
          openstack.yml
          swift.yml

- **group_name.yml** - Copy all of the ``/rhel-osp/inventory/group_vars/group_name.yml``
  files to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the ``/roles/some_role/defaults``
and ``/roles/some_role/vars`` folders. Typically only the ``/roles/some_roles/defaults``
would need to be modified. Always review both sets of variables for content.

.. code-block:: bash

    /rhel-osp/roles/some_role
    -- /defaults
          main.yml
    -- /vars
          main.yml

Deploy the Red Hat OpenStack Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next run the ``rhel-osp/site.yml`` playbook to deploy RHEL OSP to the hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/rhel-osp
    ansible-playbook site.yml -i ../../inventory/hosts.ini

.. note::

    The ``site.yml`` playbook will call the following playbooks.

    The ``haproxy.yml`` playbook will create firewall rules, install and configure
    Keepalived and HAProxy.

    The ``control_plane.yml`` playbook will include a series of playbooks that will
    install and configure the control plane services.

    The ``neutron-network-node.yml`` playbook will install and configure the Neutron
    networking on the grouped hosts. It will also set the required firewall rules
    for Neutron.

    The ``compute_node.yml`` playbook will install and configure the required Nova
    Compute packages, Neutron agents and create Nova firewall rules.

    The ``swift.yml`` playbook will install and configure Swift and other required
    agents. It will also create required firewall rules for these services.

    The ``prep-scaleio.yml`` playbook will create the required firewall rules for
    use with EMC SCaleIO.


At this point RHEL OSP has been installed and configured on all hosts listed
in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
