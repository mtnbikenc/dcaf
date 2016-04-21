RHEL-OSP Module
===============

The RHEL-OSP project is intended to be utilized on a CSC DCAF bare-metal deployment
but can be used on an existing RHEL environment that meets module requirements. It
will deploy a Red Hat Enterprise Linux OpenStack Platform with High Availability.

It uses Keepalived and HAProxy to provide a highly available (HA) OpenStack cluster
that is based on the reference architecture provided by Red Hat and the RDO project.
The deployment is broken down into five different node types.

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

Create / Modify the Inventory
-----------------------------

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the bare-metal-os module but must be modified to use with RHEL-OSP.

Edit the inventory to reflect your environment.

- **hosts.ini** - Modify the ``opt/autodeploy/projects/inventory/hosts.ini`` and
  add the required :code:`[group]` sections and desired hosts. Use the
  ``opt/autodeploy/projects/dcaf/rhel-osp/inventory/hosts.ini`` as a template and
  change values as needed.

.. note::

  The :code:`hosts.ini` will contain :code:`[group]` headings that correspond to
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

Refer to the ``Configuration Reference`` section below for an example.

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses multiple variables that are managed in various files. The
``inventory/host_vars/host_name.yml`` file contains host specific variables and the
``inventory/group_vars/group_name.yml`` files contain project specific variables.

.. note::
The RHEL-OSP module has multiple types of ``hosts`` based on the RHOSP role or
  service. Copy, rename and modify the appropriate type of example_host.yml file
  as needed.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host, based on RHOSP role or service, in the hosts.ini file. Create or
  modify these files by copying the contents of the appropriate
  ``/opt/autodeploy/projects/dcaf/rhel-osp/inventory/host_vars/example_host.yml``
  and changing values as needed.

.. note::
The RHEL-OSP module has multiple ``group_name`` variable files based on the RHOSP
  role or service.

- **group_name.yml** - Copy all of the ``/opt/autodeploy/projects/dcaf/rhel-osp/inventory/group_vars/group_name.yml``
  files to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Refer to the ``Configuration Reference`` section below for an example.

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

Configuration Reference
-----------------------

Inventory Directory/File Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is how the inventory directory structure is for the RHEL-OSP module.

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

The ``rhel-osp/inventory/hosts.ini`` file only contains several :code:`[group]`
sections with hosts as an example. When the inventory is modified copy the contents
of this ``hosts.ini`` file to the ``projects/inventory/hosts.ini`` file and modify
as needed.

.. code-block:: bash

    [openstack:children]
    controller
    compute
    swift
    haproxy
    neutron-network-node
    scaleio

    # Host(s) with HAProxy role - modify as needed
    [haproxy]
    haproxy-1
    haproxy-2

    # Host(s) with Controller role - modify as needed
    [controller]
    controller-1
    controller-2
    controller-3

    [swift:children]
    swift-proxy
    swift-storage

    [swift-proxy:children]
    controller

    # Host(s) with Swift storage role - modify as needed
    [swift-storage]
    swift-1
    swift-2
    swift-3

    [sql:children]
    controller

    [keystone:children]
    controller

    [rabbitmq_cluster:children]
    controller

    [glance:children]
    controller

    [cinder:children]
    cinder-server
    cinder-volume

    [cinder-server:children]
    controller

    [cinder-volume: children]
    compute

    [controller-nova:children]
    controller

    [heat:children]
    controller

    [ceilometer-control:children]
    controller

    [ceilometer:children]
    ceilometer-control
    compute

    [horizon:children]
    controller

    [neutron:children]
    neutron-network-node
    neutron-server

    [neutron-network-node:children]
    controller

    [neutron-server:children]
    controller

    [mongodb:children]
    controller

    # Host(s) with Compute role - modify as needed
    [compute]
    compute-1
    compute-2
    compute-3

.. note::

  Do not modify a group of groups :code:`[group:children]`. These groups are defined
  by the module. Add the required hosts in the respective :code:`[group]` section
  as needed.

host_vars
~~~~~~~~~

The variables that will be applied to a specific host are stored in a ``rhel-osp/inventory/host_vars/host_name.yml`` files. There are several types of hosts examples so when
the inventory is modified copy the contents of the appropriate ``host_name.yml`` example
file to the desired ``host_name.yml`` file in the ``projects/inventory/host_vars`` folder,
rename and modify it as needed for each host in the ``hosts.ini`` file.

.. code-block:: yaml

    /rhel-osp/inventory/
    -- /host_vars
          example-compute-host.yml
          example-controller.yml
          example-haproxy.yml
          example-network-node.yml
          example-swift-storage.yml

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
having to specify them individually. The group_vars variables are in the
``rhel-osp/inventory/group_vars/`` folder.

Edit these files as needed for your environment. Review all the variables but it
is recommended to only change what is required.

.. code-block:: yaml

    /rhel-osp/inventory/
    -- /group_vars
          ceilometer.yml
          cinder.yml
          haproxy.yml
          neutron.yml
          openstack.yml
          swift.yml

Variables in Roles
~~~~~~~~~~~~~~~~~~

Ansible roles allow you to organize playbooks and reuse common configuration steps
between different types of hosts. A role will allow you to define what a host is
supposed to do, instead of having to specify the steps needed to get a server
configured a certain way. Role specific variables are stored in the role/vars
directory.
