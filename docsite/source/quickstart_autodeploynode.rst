Autodeploynode Module Quick Start Guide
=======================================

This Quick Start Guide describes how to use CSC DCAF Automation to provision and
configure the Autodeploynode. It uses the following resources:

- `dcaf/autodeploynode <https://github.com/csc/dcaf/autodeploynode>`_ - To
  provision the CSC DCAF Autodeploynode which is used as the basis for all CSC
  DCAF automation. The Autodeploynode contains all the automation resources and
  is used to perform all automation tasks.

- `Hanlon <https://github.com/csc/Hanlon>`_ - As an advanced provisioning
  platform which can provision both bare-metal and virtual systems.

Before You Begin
----------------

Ensure that the following requirements are met:

User Access Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve the automation resources from their online locations you will need
the following:

A user account on the vendor websites with access to download the desired resources.

- Red Hat account with a valid subscription

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

The Autodeploynode has the following requirements:

- Deployed on a dedicated physical device with OOB management or a virtual
  machine with remote access
- Has an IP address on the PXE network
- At least 128GB HDD (SSD)
- Dual core CPU
- 16GB RAM

Create the Autodeploynode
-------------------------

The AutoDeployNode is the central location for all CSC DCAF automation resources.
Once the OS has been installed, CSC DCAF will be used to provision and configure
the rest of the automation resources.

Install the OS
~~~~~~~~~~~~~~

Install the desired version of RHEL OS. This can be on a physical or virtual
machine as long as all requirements are met. Be sure to set the hostname and
static ip address.

For information on how to install Red Hat refer to the `Red Hat Enterprise Linux
Installation Guide <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/sect-installation-graphical-mode-x86.html>`_.

For more information on setting a static ip address refer to the `networking
guide using the command line interface <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/sec-Using_the_Command_Line_Interface.html>`_.

Configure the Autodeploynode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The remainder of the Autodeploynode configuration is scripted and can be run
after a few environment variables have been set. The build script stages and
configures the Autodeploynode. Review the script for more details of all the
steps which are performed.

Set the environment variables for Red Hat Subscription Manage credentials:
​
.. code-block:: bash

    export RHN_USER="username"
    export RHN_PASS="password"    # escape dollar signs (\$)
    export RHN_POOL="pool_id"     # 32-char pool ID

With the environment variables defined the build script can be launched:
​

.. code-block:: bash

    curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash​

.. note::

    The build.sh script will perform a complete configuration of the Autodeploynode
    using all project defaults. If there are changes required for your environment,
    a manual installation should be performed. Refer to the CSC DCAF project
    documentation for more details.

At this point the Autodeploynode has been deployed and is ready to start using
for automation.
