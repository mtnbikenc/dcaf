# Prep-projects Role

The prep-projects role will prepare a particular project for use once the Autodeploynode
has been staged. It includes project based .yml files as needed based on a `use_project`
variable found in the `inventory/group_vars/autodeploynode.yml`.

For each project included in the role there must be a `project_name.yml` file in 
the `prep-projects/tasks` folder. That `project_name.yml` file will provide the
actions necessary to prepare the project for use.

The `prep-projects/tasks/main.yml` file must have an include statement for each 
`project_name.yml` file.

## Requirements

The role requires a pre-installed version of the RHEL OS on the Autodeploynode.

## Role Variables

The variables for this role come from facts gathered by Ansible and the 
`inventory/group_vars/autodeploynode.yml`. The `autodeploynode.yml` variables can
be edited as needed.

## Dependencies

The role depends on the requirements listed above.

## Playbook

The role is called in the `dcaf/modules/autodeploynode/autodeploy.yml` playbook.
