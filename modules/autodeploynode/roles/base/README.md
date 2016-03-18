Base Role
=========

This role will prepare the AutoDeployNode with the all the resources needed to
to use CSC DCAF. It will install the necessary packages, configure them and
clone the required git repositories.

Requirements
------------

The role requires a pre-installed version of RHEL with internet connectivity
performed from the instructions provided in this repository.

Role Variables
--------------

The variables for this role come from facts gathered by ansible and
vars/main.yml. The vars/main.yml variables need to be edited as needed.

Dependencies
------------

The role depends on the requirements listed above.

Playbook
--------

The role is called in the main.yml playbook.

Run the playbook from the dcaf/modules/autodeploynode directory

    ansible-playbook main.yml
