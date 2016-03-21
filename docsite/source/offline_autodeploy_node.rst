AutoDeployNode Creation - Offline Mode
======================================

In offline mode a :code:`staging node` will be used to download all automation
resources and prepare them to be staged on the offline AutoDeployNode. The
:code:`staging node` can be an existing instance of RHEL or a new installation.
In either case be sure it meets the defined requirements in the ``Offline Staging Node``
section of http://csc.github.io/dcaf/requirements.html for more information.

Prepare the Staging Node
------------------------

When offline mode is used the :code:`staging node` is used to gather the automation
resources and put them on a portable USB hard drive so they can be used by the
offline AutoDeployNode.

Prepare the USB Hard Drive
~~~~~~~~~~~~~~~~~~~~~~~~~~

Login as a user with elevated privileges and connect the USB hard drive. Once
connected Linux will add a new block device into the :code:`/dev/` directory. The
drive needs to be mounted by the OS. To find out the name given to the USB drive
run the following :code:`fdisk` command:

.. code-block:: bash

    fdisk -l
    Disk /dev/sdb: 20.0 GB, 20000268288 bytes
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    Disk identifier: 0x000b2b03

.. note::

    The name of the connected device - in the above example it is :code:`sdb`.
    Substitute your connected device name in its place if needed.

Now create the local directory within Linux where the USB drive will be mounted.
Use the device name from the :code:`fdisk` command in the previous step, our
example was :code:`sdb`

.. code-block:: bash

    mkdir /mnt/sdb

Now run the mount command and mount the drive:

.. code-block:: bash

    mount /dev/sdb /mnt/sdb

Leave the USB drive connected until all the automation resources have been
downloaded at the end of the following section.

Stage Resources to Staging Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/offline_stage.sh | bash​

.. note::

    The offline_build.sh script will stage all automation project resources to
    itself then copy them to the USB hard drive. Refer to the DCAF project
    documentation for more details.

At this point the automation resources have been staged to the USB hard drive.

Unmount the USB hard drive and disconnect it from the :code:`staging node`.

.. code-block:: bash

    umount /dev/sdb

Create the Offline AutoDeployNode
---------------------------------

The offline AutoDeployNode will be created on a physical or virtual device connected
to an air-gapped network. The support packages and other automation resources will
be installed from the portable USB hard drive where they were saved.

Install the RHEL OS
~~~~~~~~~~~~~~~~~~~

The RHEL OS can be installed by attaching the ISO image with the vendor supplied
management utility or whatever other method is available.

.. note::

    For more information on attaching an ISO image refer to the vendor documentation.

On the installation summary page, you may see different selections with yellow
exclamation or warning marks.

These are areas that require some setup:

.. code-block:: bash

   Date & Time : Current Date / Time ? Time Zone
   Installation Source : Local Media
   Software Selection : Minimal Install
   Installation Destination : Partitioning : Automatically configure partitioning
   Network & Hostname : Enable the network interface and configure with relative
   static network information
   Root Password : Set the root password
   Create User: autodeploy

Here is a link to the Red Hat Install guide https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/sect-installation-graphical-mode-x86.html

Set the Static IP
~~~~~~~~~~~~~~~~~

Boot the AutoDeployNode and configure the network interface with a static IP address.

.. code-block:: bash

    vi /etc/sysconfig/network-scripts/ifcfg-your_interface

Modify the file, where ``ifcfg-interface`` is the management network interface, to
resemble the example below with your specific network configuration.

.. code-block:: bash

    BOOTPROTO="none"
    ONBOOT=yes
    IPADDR=x.x.x.x
    NETMASK=x.x.x.x
    GATEWAY=x.x.x.x
    DNS1=x.x.x.x

For more information on configuring the network refer to the  https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/sec-Using_the_Command_Line_Interface.html document.

Set the Hostname
~~~~~~~~~~~~~~~~

Next configure the hostname:

.. code-block:: bash

    hostnamectl set-hostname autodeploy.local

Stage the Automation Resources on AutoDeployNode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that the OS has been installed it is time to stage the automation resources.

Login as a user with elevated privileges and connect the USB hard drive. Once
connected Linux will add a new block device into the :code:`/dev/` directory. The
drive needs to be mounted by the OS. To find out the name given to the USB drive
run the following :code:`fdisk` command:

.. code-block:: bash

    fdisk -l
    Disk /dev/sdb: 20.0 GB, 20000268288 bytes
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    Disk identifier: 0x000b2b03

.. note::

    The name of the connected device - in the above example it is :code:`sdb`.
    Substitute your connected device name in its place if needed.

Now create the local directory within Linux where the USB drive will be mounted.
Use the device name from the :code:`fdisk` command in the previous step, our example
was :code:`sdb`

.. code-block:: bash

    mkdir /mnt/sdb

Now run the mount command and mount the drive:

.. code-block:: bash

    mount /dev/sdb /mnt/sdb

Next copy the automation resources from the USB drive to the :code:`/opt/` directory.

.. code-block:: bash

    cp -r /mnt/sdb1/autodeploy* /opt
    chown -R autodeploy /opt/autodeploy/

Now that files exist locally on the AutoDeployNode the local repository needs to
be configured.

Configure the Offline RPM Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The required RPM packages were staged on the AutoDeployNode in the
:code:`/opt/autodeploy/resources/rpms` directory. The offline repository was
created in this directory using the :code:`createrepo` utility. To configure
:code:`yum` to use it, copy the local.repo file into the :code:`/etc/yum.repos.d/`
directory.

.. code-block:: bash

    cp /opt/autodeploy/projects/dcaf/modules/autodeploynode/files/local.repo /etc/yum.repos.d/

Check to see that the repo is listed:

.. code-block:: bash

    yum repolist
      local_repo

Install the Required Support Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next install Git and Ansible to be used for automation. Ansible is installed from
the rpm file created in the staging process found in the offline repository.

.. code-block:: bash

    yum -y install git ansible

Run the DCAF Base Playbooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that the variables have been configured, run the following playbooks to
finish the AutoDeployNode deployment.

.. code-block:: bash

    cd /opt/autodeploy/projects/dcaf/modules/autodeploynode
    ansible-playbook main.yml

The :code:`main.yml` playbook will also run the :code:`site_docker.yml` and
:code:`site_discovery.yml` playbooks.

The :code:`site_docker.yml` playbook will start the Hanlon Docker environment.
First it will clean up any existing containers. Then it will start the Mongo,
Hanlon Server and TFTP Server containers.

The :code:`site_discovery.yml` playbook will configure the DHCP service and
prepare the Hanlon Server for the bare metal OS deployment.

At this point the AutoDeployNode has been configured and is ready to start using
for automation.

