# Createrepo Role

The createrepo role will prepare an http repository on the Autodeploynode when
it used in offline mode. When used in `offline mode` all the necessary packages are
downloaded to the `/opt/autodeploy/resources/rpms` directory. This directory is
used for both a local and an apache based http repository.

The role will do the following:
  * Create an offline repo file in the repository that can be distributed to any
    hosts `/etc/yum.conf` directory.
  * Create an offline repo config for apache and puts it in the
    `/etc/httpd/conf.d` directory.
  * Restart the httpd service so the changes take effect.

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
