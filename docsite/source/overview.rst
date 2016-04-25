Overview
========

The CSC Data Center Automation Framework `(DCAF) <https://github.com/csc/dcaf>`_
is a collection of resources designed to automate various platforms and deployments
within the data center. It is based on `Ansible <http://docs.ansible.com/ansible/index.html>`_
automation. Ansible in short is an automation platform that can configure, deploy
and orchestrate IT tasks.

CSC DCAF is comprised of CSC public open source projects, and various community
based open source projects.

CSC DCAF and Ansible Automation
-------------------------------

As previously mentioned the CSC DCAF project is based on Ansible automation. It
follows the Ansible hierarchy, best practices and uses their pre-written modules.

The key things to note about Ansible are:

- `Inventory <http://docs.ansible.com/ansible/intro_inventory.html>`_ contains
  the hosts that Ansible will execute against and the configuration variable
  files. The inventory is configurable and can customized to your environment.

- `Playbooks <http://docs.ansible.com/ansible/playbooks.html>`_ are Ansible's
  configuration, deployment and orchestration language. They are used to manage
  configurations of and deployments to remote machines. They are written in YAML
  syntax.

Ansible Inventory
~~~~~~~~~~~~~~~~~

The inventory for CSC DCAF is located in the ``/opt/autodeploy/projects/inventory``
folder. It follows the Ansible inventory hierarchy:

.. code-block:: none

    /inventory
    -- /group_vars
          all.yml
          group_name.yml
    -- hosts.ini
    -- /host_vars
          host_name.yml

- **hosts.ini** - The inventory file that contains the names of the hosts Ansible
  will execute against. Hosts can be grouped by adding a :code:`[group]` section
  heading and placing desired hosts under it. Groups can also be grouped the same
  way.

 **Example:**

.. code-block:: yaml

    [groups:children]
    group1
    group2

    [group1]
    host1
    host2

    [group2]
    host3

  - **host_name.yml** - There should be a ``host_name.yml`` file for each host in the
  ``hosts.ini`` file. This file will contain variables that will be assigned to the
  host when the playbook runs.

- **all.yml** - This file contains variables that apply to all hosts in the
  ``hosts.ini``. These are referred to as global variables.

- **group_name.yml** - This file can be used to specify variables that only get
  to the ``group`` in the ``hosts.ini`` file. The name of this file must match the
  name of the :code:`[group]` in the ``hosts.ini`` file.

Refer to the Ansible `Inventory <http://docs.ansible.com/ansible/intro_inventory.html>`_
for additional information.

CSC DCAF Projects & Modules
---------------------------

The CSC DCAF project is kept under source control in a GitHub repository and includes
the following CSC modules:

- `Autodeploynode <https://github.com/csc/dcaf/autodeploynode>`_ - Provisions and
  and configures the CSC DCAF Autodeploynode.

- `Bare-Metal-OS <https://github.com/csc/dcaf/bare-metal-os>`_ - An automated
  deployment of an operating system to bare-metal hardware using Hanlon, currently
  the Red Hat Enterprise Linux OS.

- `KVM-Host <https://github.com/csc/dcaf/kvm-host>`_ - An automated deployment and
  configuration of virtual machines on RHEL KVM hosts.

- `RHEL-OSP <https://github.com/csc/dcaf/rhel-osp>`_ - An automated deployment of
  a Red Hat OpenStack Cluster with high availability.

- `Vmware <https://github.com/csc/dcaf/vmware>`_ - An automated deployment of
  a VMware Virtual Infrastructure on bare-metal hardware.

CSC DCAF leverages additional CSC open source projects which are also kept under
version control in GitHub repositories:

`Hanlon <https://github.com/csc/Hanlon>`_ - An advanced provisioning application
which can deploy both bare-metal and virtual systems.

`Slimer <https://github.com/csc/slimer>`_ - The CSC Slimer project, a fork of
`abrezhnev/slimer <https://github.com/abrezhnev/slimer>`_, is used to deploy
the Red Hat OpenStack Platform with high availability on base RHEL installations.

`Ansible-ScaleIO <https://github.com/csc/ansible-scaleio>`_ - The CSC
Ansible-ScaleIO project, a fork of `sperreault/ansible-scaleio <https://github.com/sperreault/ansible-scaleio>`_, is used to install, configure and manage ScaleIO.
When used with DCAF, this project adds EMC ScaleIO storage capabilities to the
Red Hat OpenStack Platform.

The Autodeploynode
------------------

The main component of CSC DCAF is the **Autodeploynode**. This node contains all
the source files and dependencies to support operation of the framework to:

* **Discover** new nodes that are added to the pod. This process of automated
  discovery is driven by the Hanlon instance that is running on the Autodeploynode
  (and a default, discover-only policy that has been added to that Hanlon instance).
* **Provision** new operating systems or hypervisors to those nodes. This process
  of policy-based provisioning is driven using Ansible and Hanlon, with Ansible
  creating the policies necessary to provision the right OS/hypervisor to the right
  node at the right time.
* **Deploy** new platforms into the OS/hypervisor instances that were provisioned
  to those nodes. The process of platform deployment is driven using Ansible.
* **Configure** the infrastructure associated with the pod, the nodes in the pod,
  and the platforms deployed to those nodes. The process of configuration at the
  infrastructure, OS/hypervisor, and platform layer is driven using Ansible.

As detailed in the documentation, the build of the Autodeploynode is automated
through scripts and Ansible playbooks.

The Autodeploynode can be deployed as a virtual machine or on physical hardware
with Red Hat Enterprise Linux as the base operating system. Docker containers are
used to stand up the Hanlon instance and it's requirements, MongoDB and a TFTP
server. In order to automatically discover and provision physical hardware, a DHCP
server is configured to provide addresses on the local subnet. Ansible is used as
the automation tool to deploy and configure systems and applications.
