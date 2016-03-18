CSC DCAF Automation Quick Start Guide
=====================================

This quick start guide describes how to use the following CSC DCAF Automation
projects:

- **DCAF Modules**
  - **Base** Provisions a CSC DCAF AutoDeployNode which is used as the
  basis for all DCAF automation. The AutoDeployNode contains all the automation
  resources and is used to perform all automation tasks.
  - **Bare-Metal-OS** - Provides an automated bare-metal deployment of the
    Red Hat Enterprise Linux OS using Hanlon.
- **Hanlon** - Hanlon is an advanced provisioning platform which can provision
  both bare-metal and virtual systems.
- **Slimer** - Slimer is a fork of abrezhnev/slimer to deploy the Red Hat
  OpenStack Platform with high availability DCAF provisioned RHEL
  installations.
- **Ansible-ScaleIO** - Ansible-ScaleIO is a fork of sperreault/ansible-scaleio
  to install, configure and manage ScaleIO. ScaleIO provides additional storage
  capabilities to the Red Hat OpenStack Platform.

Before You Begin
----------------

Ensure that the following requirements are met:

User Access Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve the automation resources from their online repositories you will
need the following:

- A valid github.com user account with access to the CSC Git repositories.
- A Red Hat user account with a valid subscription associated with it.

Network Requirements
~~~~~~~~~~~~~~~~~~~~

There are several network requirements for the deployment.

- DNS server IP addresses need to be provided
- NTP server IP address needs to be provided
- The following VLANS are required:
  - Out-of-band management (IPMI)
  - PXE Network
- Out-of-band Network IP address for each node
- Management IP address for each node.
- The AutoDeployNode has internet access and DNS

Physical Hardware
~~~~~~~~~~~~~~~~~

CSC DCAF was developed and tested with the following hardware

- DELL PowerEdge 630 | PowerEdge 730
- DELL PERC H730 RAID Controller

Target Deployment Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The target deployment environment consists of all nodes that will participate in
the deployment.

- The physical hardware has been installed and connected to the network
- A 1GB connection for OOB management on the management switch
- 2 10GbE connections to the 10GbE network switches
- The upstream and management network have already been configured
- An on-site resource to configure the out-of-band management IP addresses.

Create the AutoDeployNode
-------------------------

The AutoDeployNode is the central location for all CSC DCAF automation projects.
Once an OS has been installed, DCAF will be used to provision and configure the
rest of the DCAF Automation resources.

Install the RHEL OS
~~~~~~~~~~~~~~~~~~~

Install the desired version of RHEL OS. This can be on a physical or virtual
machine as long as all requirements are met. Be sure to set the hostname and
static ip address.

For information on how to install Red Hat refer to the `Red Hat Enterprise Linux
Installation Guide <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/sect-installation-graphical-mode-x86.html>`_.

For more information on setting a static ip address refer to the `networking
guide using the command line interface <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/sec-Using_the_Command_Line_Interface.html>`_.

Configure the AutoDeployNode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The remainder of the AutoDeployNode configuration is scripted and can be run
after a few environment variables have been defined. The build script provisions
and configures the AutoDeployNode. Review the script for more details of all the
steps which are performed.

Set the environment variables for Red Hat Subscription Manage credentials:
​

.. code-block:: bash

    export RHN_USER="username"
    export RHN_PASS="password"    # escape dollar signs (\$)
    export RHN_POOL="pool_id"     # 32-char pool ID

Create a ssh key file for GitHub access.  Put the text for a private key which
has access to the GitHub repositories in the lines below:

.. code-block:: bash

    cat << EOF > ~/github.pem
    -----BEGIN RSA PRIVATE KEY-----
    <insert_key_file_text_here>
    -----END RSA PRIVATE KEY-----
    EOF

Change the file permissions to ensure security.

.. code-block:: bash

    chmod 0600 ~/github.pem

With the environment variables defined and the ssh key file created, the build
script can be launched:
​

.. code-block:: bash

    curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash​

.. note::

    The build.sh script will perform a complete configuration of the AutoDeployNode
    using all project defaults. If there are changes required for your environment,
    a manual installation should be performed. Refer to the DCAF project
    documentation for more details.

At this point the AutoDeployNode has been deployed and is ready to start using
for automation.

Run CSC DCAF Automation
-----------------------

The current CSC DCAF Automation is run from the bare-metal-os module and is
configured to use Slimer and Ansible-ScaleIO. This will deploy Red Hat OpenStack
with HA and ScaleIO on a base RHEL OS as follows:

- 3 - Controller nodes
- 1 - Compute node
- 3 - Swift nodes
- 3 - ScaleIO nodes

Before the automation can be used the source configuration needs to be sanitized
and configured for the deployment environment.

Create the Inventory
~~~~~~~~~~~~~~~~~~~~

There are two parts to the inventory, the :code:`hosts.ini`` and the :code:`host.yml`.
For more information and an example :code:`host.yml` file see the DCAF project
documentation.

- **hosts.ini** - edit the :code:`dcaf/modules/bare-metal-os/inventory/hosts.ini` file. There are
  existing [group] sections based on the role that the host should have.
- **hostname.yml** - There should be a :code:`dcaf/modules/bare-metal-os/inventory/host_vars/hostname.yml`
  for each host in the hosts.ini file. Use the :code:`dcaf/modules/bare-metal-os/inventory/host_vars/example_host.yml`
  as a template and change values as needed.

.. note::

    Each ``host.yml`` file must include the host hardware ``smbios-uuid``.
    This can be done using the hosts vendor management tools. Refer to the vendor
    documentation for more information.

Update Group Variables
~~~~~~~~~~~~~~~~~~~~~~

Review the :code:`dcaf/modules/bare-metal-os/inventory/group_vars/all.yml` file
and modify as needed. It defines variables used deployment-wide.

Prepare Hosts for Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the :code:`dcaf/modules/bare-metal-os/site_reset.yml` playbook to power
cycle the hosts and have them discovered by Hanlon:
​

.. code-block:: bash

    ansible-playbook site_reset.yml

Run the Deployment Playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the :code:`dcaf/modules/bare-metal-os/site.yml` playbook. This will deploy
the RHEL OS, run Slimer to deploy Red Hat OpenStack with HA and run
Ansible-ScaleIO to deploy EMC ScaleIO.

.. code-block:: bash

    ansible-playbook site.yml
