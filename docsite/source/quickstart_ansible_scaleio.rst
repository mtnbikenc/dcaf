Ansible-ScaleIO Quick Start Guide
=================================

This Quick Start Guide describes how to use CSC DCAF Automation to deploy the EMC
ScaleIO storage solution on Red Hat OpenStack Platform. It uses the following resources:

- `Ansible-ScaleIO <https://github.com/csc/ansible-scaleio>`_ - The CSC Ansible-ScaleIO
  project, a fork of `sperreault/ansible-scaleio <https://github.com/sperreault/ansible-scaleio>`_,
  is used to install, configure and manage EMC ScaleIO. When used with CSC DCAF, this
  project adds EMC ScaleIO storage capabilities to the Red Hat OpenStack Platform.

The Ansible-ScaleIO project is intended to be utilized on a CSC DCAF deployment of
the Red Hat OpenStack Platform.

Before You Begin
----------------

Ensure that the following requirements are met:

  - A user account on the EMC website to download the software.
  - Download the EMC ScaleIO software (version 1.32.2 is currently supported).
    Be sure to download the supported version.

Run the Ansible-ScaleIO Automation
----------------------------------

To use the Ansible-ScaleIO automation download the required software, modify the
inventory and variables then run the playbook.

Download the EMC ScaleIO Software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the following software from the EMC website to the ``/opt/autodeploy/resources/scaleio`` folder. The automation will handle the extrating and placement of files.

  - ScaleIO_1.32.2_Gateway_for_Linux_Download.zip
  - ScaleIO_1.32.2_OpenStack_Driver_Download.zip
  - ScaleIO_1.32.2_RHEL7_Download.zip

Modify the Inventory
~~~~~~~~~~~~~~~~~~~~

The inventory is managed by the ``hosts.ini`` file. The inventory should have been
created by a previous module or project but must be modified to use with Ansible-ScaleIO.
For more information and examples of this file refer to the CSC DCAF project documentation.

Edit the inventory to reflect your environment.

- **hosts.ini** - Modify the ``/opt/autodeploy/projects/inventory/hosts.ini`` and
  add the required :code:`[group]` sections and desired hosts. Use the
  ``/opt/autodeploy/projects/ansible-scaleio/inventory/hosts.ini`` as a template
  and change values as needed.

.. note::

    The ``hosts.ini`` will contain :code:`[group]` headings that correspond to
    EMC ScaleIO roles. Each :code:`[group]` heading will contain a host or a child
    ``group`` of hosts. If editing this file append to it and ensure there is no
    duplication. All hosts listed should be under a :code:`[group]` heading.

.. code-block:: yaml

    Example:
    # Host(s) with the MDM role
    [mdm]
    host-1
    ...

    # Host(s) with the TB role
    [tb]
    host-2
    ...

.. note::

    Do not modify a group of groups :code:`[group:children]`. These groups are defined
    by the module. Add the required hosts in the respective :code:`[group]` section
    as needed.

Modify Host & Project Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses multiple variables that are managed in various files. The
``host_vars/host_name.yml`` file contains host specific variables and the ``group_vars/common.yml`` file contains project specific variables.

- **host_name.yml** - There should be a ``/opt/autodeploy/projects/inventory/host_vars/host_name.yml``
  file for each host in the hosts.ini file. These files were created by the Red Hat
  OpenStack deployment. They should not have to be modified but should be reviewed
  for content.

- **common.yml** - Copy the ``/opt/autodeploy/projects/ansible_scaleio/inventory/group_vars/common.yml``
  file to the ``/opt/autodeploy/projects/inventory/group_vars/`` folder, rename it
  ``ansible_scaleio.yml`` and modify as needed per the environment.

Install EMC ScaleIO
~~~~~~~~~~~~~~~~~~~

Next run the ``ansible_scaleio/site.yml`` playbook to install and configure ScaleIO
on the hosts in inventory:

.. code-block:: bash

    cd /opt/autodeploy/projects/ansible_scaleio
    ansible-playbook site.yml -i ../inventory/hosts.ini

At this point EMC ScaleIO has been installed and configured on all hosts specified
in the ``/opt/autodeploy/projects/inventory/hosts.ini``.
