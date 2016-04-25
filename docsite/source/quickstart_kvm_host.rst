KVM-Host Quick Start Guide
==========================

This Quick Start Guide describes how to use CSC DCAF Automation to deploy and
configure virtual machines on RHEL KVM hosts. It uses the following resources:

- `dcaf/kvm-host <https://github.com/csc/dcaf/kvm-host>`_ - An automated deployment
  and configuration of virtual machines on RHEL KVM hosts.

The KVM-Host project is intended to be utilized on a CSC DCAF bare-metal OS deployment.

Before You Begin
----------------

Ensure that the following requirements are met:

Need to determine the requirements.

Run the KVM-Host Automation
---------------------------

To use the KVM-Host automation modify the inventory and variables then run the playbook(s).

Modify the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory was created
by the bare-metal-os module but must be modified to use with KVM-Host. For more
information and examples of this file refer to the CSC DCAF project documentation.

Edit the inventory to reflect your environment.

- **hosts.ini** - Modify the ``opt/autodeploy/projects/inventory/hosts.ini`` and
  add the required :code:`[group]` sections and desired hosts. Use the
  ``opt/autodeploy/projects/dcaf/kvm-host/inventory/hosts.ini`` as a template and
  change values as needed.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    RHOSP and module roles. Each :code:`[group]` heading will contain a host or a child
    ``group`` of hosts. If editing this file append to it and ensure there is no
    duplication. All hosts listed should be under a :code:`[group]` heading.

.. code-block:: yaml

    Example:
    # KVM host machine(s)
    [kvmhosts]
    kvm-controller-1
    ...

    # VM(s) to be created
    [nodes]
    controller-1
    compute-1
    ...

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module uses multiple variables that are managed in various files. The
``host_vars/host_name.yml`` file contains host specific variables and the
``group_vars/kvm-hosts.yml`` file contains module specific variables.

.. note::

    The KVM-Host module has two types of ``hosts``, one is the physical host ``(kvm-host)``
    and the virtual host ``(vm)``. Copy, rename and modify the appropriate type of example
    host file as needed.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  for each host, physical and virtual, in the hosts.ini file. Create or modify these
  files by copying the contents of the appropriate ``/opt/autodeploy/projects/dcaf/rhel-osp/inventory/host_vars/example_kvmhost.yml``
  or ``/opt/autodeploy/projects/dcaf/kvm-host/inventory/host_vars/example_vm.yml``
  and modifying as needed.

- **kvm-hosts.yml** - Copy the ``/opt/autodeploy/projects/dcaf/kvm-host/inventory/group_vars/kvm-hosts.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder and modify
  as needed per the environment.

Deploy VMs on KVM
~~~~~~~~~~~~~~~~~

Next run the ``kvm-host/site.yml`` playbook to deploy VMs on the hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/modules/kvm-host
    ansible-playbook site.yml -i ../../inventory/hosts.ini

At this point all VMs have been deployed on all KVM hosts listed in the
``/opt/autodeploy/projects/inventory/hosts.ini``.
