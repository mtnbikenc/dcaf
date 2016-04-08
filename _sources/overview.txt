Overview
========

The CSC Data Center Automation Framework (DCAF) is a collection of resources
designed to automate various platforms and deployments within the data center.
It is comprised of CSC public open source projects, and various community based
open source projects.

Project Sources
---------------

`CSC DCAF <https://github.com/csc/dcaf>`_ is a collection of resources designed
to automate various platforms and deployments within the data center. It is kept
under source control in a GitHub repository and includes the following CSC modules:

- `Autodeploynode <https://github.com/csc/dcaf/autodeploynode>`_ - Provisions and
  and configures the CSC DCAF Autodeploynode.

- `Bare-metal-OS <https://github.com/csc/dcaf/bare-metal-os>`_ - An automated
  deployment of an operating system to bare-metal hardware using Hanlon, currently
  the Red Hat Enterprise Linux OS.

- `Kvm-host <https://github.com/csc/dcaf/kvm-host>`_ - An automated deployment and
  configuration of virtual machines on RHEL KVM hosts.

- `Rhel-osp <https://github.com/csc/dcaf/rhel-osp>`_ - An automated deployment of
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

CSC DCAF Modes
--------------

Since CSC DCAF is a framework, it is designed to be used in two different
operational modes. The two modes are online and offline and are detailed below.

Online Mode
~~~~~~~~~~~

When CSC DCAF is used in online mode the Autodeploynode is connected to an external
network with direct access to automation resources. The CSC Decaf projects are
stored in source controlled repositories on Github and other resources such as
RPMs and ISOs are downloaded directly from the Internet.

Offline Mode
~~~~~~~~~~~~

When CSC DCAF is used in offline mode the Autodeploynode does not have external
network access and cannot get to the automation resources. For this reason
additional resources are needed and steps must be taken to prepare for an offline
Autodeploynode installation.

In offline mode all automation resources will be retrieved from the Internet by
a :code:`staging node` that has Internet access. They will be saved to a USB hard
drive connected to this node and will later be moved to the offline Autodeploynode
and used for deployment. Once this is done all projects can be used as documented.
Keep in mind that the method of retrieving the automation resources will have to
be repeated in order to obtain any updates.
