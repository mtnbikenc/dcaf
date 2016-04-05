# Base Role

This role will prepare the Autodeploynode with all the resources needed to
to use CSC DCAF automation. It will install the necessary packages, configure them
and clone the required git repositories.

## Requirements

The role requires a pre-installed version of RHEL OS with internet connectivity
performed from the instructions provided in this repository.

## Role Variables

The variables for this role come from facts gathered by Ansible and the 
`inventory/group_vars/autodeploynode.yml`. The `autodeploynode.yml` variables can be
edited as needed.

## Dependencies

The role depends on the requirements listed above.

## Playbook

The role is called in the `dcaf/modules/autodeploynode/autodeploy.yml` playbook.
