Autodeploynode Module
=====================

The **Autodeploynode** is the main component of CSC DCAF project. This node contains
all the source files and dependencies to support operation of the framework. It is
connected to an external network with direct access to automation resources. Since
our projects have multiple dependencies we have automated the process to install
and configure the Autodeploynode as much as possible.

Before You Begin
----------------

Ensure that the following requirements are met:

    - It can be deployed on a physical or virtual machine
    - It has an IP address on the PXE & IPMI Network
    - At least 50GB of available disk space
    - Red Hat user account with a valid subscription (to download the ISO)

Install the RHEL OS
-------------------

The first step is to install RHEL. This can be a physical or virtual machine as
long as all the requirements are met.

Download the appropriate version of the RHEL ISO file and save it somewhere that
can be accessed by the Autodeploynode. Use the vendor management tools to attach
the ISO file and boot to it.

On the installation summary page, you may see different selections with yellow
exclamation or warning marks. These are areas that require some setup:

.. code-block:: none

    Date & Time : Current Date / Time ? Time Zone
    Installation Source : Local Media
    Software Selection : Minimal Install
    Installation Destination : Partitioning : Automatically configure partitioning
    Network & Hostname : Enable the network interface and configure with relative
    static network information
    Root Password : Set the root password
    Create User: autodeploy

Here is a link to the `Red Hat Install guide <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/sect-installation-graphical-mode-x86.html>`_

Set the Static IP
~~~~~~~~~~~~~~~~~

Boot the Autodeploynode and configure the network interface with a static IP address.
For more information refer to the `networking guide using the command line interface <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/sec-Using_the_Command_Line_Interface.html>`_.


.. code-block:: bash

    vi /etc/sysconfig/network-scripts/ifcfg-<nic>

Modify this file to resemble this configuration with your specific network
configuration.

.. code-block:: bash

    BOOTPROTO="none"
    ONBOOT=yes
    IPADDR=x.x.x.x
    NETMASK=x.x.x.x
    GATEWAY=x.x.x.x
    DNS1=x.x.x.x

Set the Hostname
~~~~~~~~~~~~~~~~

Next configure the hostname:

.. code-block:: bash

    hostnamectl set-hostname autodeploy.local

Now that the OS has been installed it is time to stage the automation resources.

Configure Autodeploynode
------------------------

The Autodeploynode is responsible for all automation resources for a given project
or module. The base CSC DCAF resources will be staged directly to it as part of
the configuration.

Scripted Install
~~~~~~~~~~~~~~~~

The build of the Autodeploynode is scripted and can be run after a few environment
variables have been defined. It will need to install packages and download files
needed by RHEL so it needs to be registered with subscription-manager. Environment
variables for Red Hat Subscription credentials should be defined:

.. code-block:: bash

    export RHN_USER="username"
    export RHN_PASS="password" # escape dollar signs (\\$)
    export RHN_POOL="pool_id" # 32-char pool ID

With the environment variables defined, the build script can be launched:

.. code-block:: bash

    curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash

Review the details in the build script for a description of tasks performed to build
the Autodeploynode.

.. note::

    The :code:`build.sh` script will perform a complete stage and configuration
    of the Autodeploynode using all project defaults. If there are changes required
    for your environment, a manual installation should be performed.

Manual Install
~~~~~~~~~~~~~~

The Autodeploynode will need to install packages and download files needed by RHEL
so it needs to be registered with subscription-manager.

Register with Subscription Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most commands require elevated privileges so you may need to :code:`su -`. Register
with Red Hat Subscription Manager. Fill in the username and password with credentials
that have a valid Red Hat subscription associated with it.

.. code-block:: bash

    su -
    subscription-manager register --username=your_user --password=your_password

Find one of the repositories that include "Red Hat Openstack". Once a subscription
is found that provides Openstack note the "Pool ID"

.. code-block:: bash

    subscription-manager list --all --available
    subscription-manager attach --pool="Pool ID"

Disable all repositories, then enable RPM repositories as needed.

.. code-block:: bash

    subscription-manager repos --disable=*
    subscription-manager repos --enable=rhel-7-server-rpms \
    --enable=rhel-7-server-optional-rpms \
    --enable=rhel-7-server-extras-rpms \
    --enable=rhel-7-server-openstack-6.0-rpms \
    --enable=rhel-server-rhscl-7-rpms \
    --enable=rhel-ha-for-rhel-7-server-rpms

Install Support Packages
^^^^^^^^^^^^^^^^^^^^^^^^

Next install the required support packages; ``epel-release, git and wget.``

.. code-block:: bash

    yum -y install https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-6.noarch.rpm
    yum -y install git wget

Install Ansible
^^^^^^^^^^^^^^^

.. note::

    Ansible v2.0 is currently not available from EPEL and must be installed from
    source.

To build an Ansible RPM from source, additional packages are required:

.. code-block:: bash

    yum -y install rpm-build make asciidoc python2-devel python-setuptools

Now the source for Ansible must be cloned. A particular version of Ansible is
currently tested and supported for use, as indicated below. The new RPM is
installed as well as additional Ansible dependencies.

.. code-block:: bash

    git clone git://github.com/ansible/ansible.git --recursive
    cd ansible/
    git checkout v2.0.1.0-1
    git submodule update --init --recursive
    make rpm
    yum -y --nogpgcheck localinstall ./rpm-build/ansible-*.noarch.rpm
    cd ..

Stage the CSC DCAF Project Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ansible has been installed and will be used to perform an automated download of
the CSC DCAF project resources. First we need to download the ``initial_stage``
playbook from the ``dcaf`` Git repository.

.. code-block:: bash

    wget https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/initial_stage.yml

Now the initial_stage.yml playbook can be run, as shown below:

.. code-block:: bash

    ansible-playbook initial_stage.yml

Now that the CSC DCAF project has been retrieved the Autodeploynode module can be
used to install the remaining support packages. Change into the Autodeploynode
module directory.

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/modules/autodeploynode

Next run the ``stage_resources.yml`` playbook to download the remaining CSC DCAF
automation resources. The ``stage_resources.yml`` play requires a valid user account
for Red Hat as outlined in the ``User Access Requirements`` section of
http://csc.github.io/dcaf/requirements.html. Before you run the play change edit
the following variables in the ``inventory/group_vars/all.yml`` file.

.. code-block:: yaml

    # Required User Variables
    rhn_user:
    rhn_pass:

Run the stage_resources.yml playbook:

.. code-block:: bash

    ansible-playbook stage_resources.yml

Configure DCAF Base variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that the Autodeploynode has the CSC DCAF resources staged it can be configured
to use other modules and projects. Before any playbooks can be run, the configuration
variables need to be edited per your environment. Configure these variables accordingly
by editing the variables in the ``dcaf/modules/autodeploynode/inventory/group_vars/all.yml``.

There following variables apply to all deployments that will need to be modified
before deployment.

By default, the DHCP server will be installed with the following configuration:

.. code-block:: yaml

    dns1: 8.8.8.8
    dhcp_start: 20
    dhcp_end: 60

.. note::

    The DHCP start and end values above are the last octet of the subnet the server
    is installed in. For example,
    172.17.16.20 would be ``dhcp_start: 20``
    172.17.16.60 would be ``dhcp_end: 60``

To use alternate values, edit the ``dcaf/modules/autodeploynode/roles/dhcp-server/defaults.yml``
file with your own values.

Running the Autodeploynode Playbook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that the variables have been configured, run the following playbooks to
finish the AutoDeployNode deployment.

.. code-block:: bash

    ansible-playbook main.yml

The ``main.yml`` playbook will run the following roles:

    - **base** - Configures the base system requirements
    - **dhcp-server** - Configures the system to run a DHCP server and sets up
      requirements for using Hanlon for discover and provisioning
    - **hanlon-docker** - Configures the Hanlon Server Docker environment
    - **hanlon-discover** - Configures the Hanlon Server to support discovery of
      nodes booted on the PXE network

.. note::

    To re-run role(s) again without running the entire ``main.yml``, tags can be
    used at the command line to run certain roles.

    ``ansible-playbook main.yml --tags=hanlon-docker,hanlon-discover``

At this point the AutoDeployNode has been configured and is ready to start using
for automation.
