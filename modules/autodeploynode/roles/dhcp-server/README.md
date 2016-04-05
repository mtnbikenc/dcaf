# Dhcp-server Role

The dhcp-server role will install and configure a DHCP server for use with IPXE 
on the Autodeploynode. 

It uses variables found in the `dhcp-server/vars/main.yml` and `dhcp-server/defaults/main.yml`.

The role will do the following:
  * Install the DHCP package via yum
  * Configure the `dhcpd.conf, ipxe.conf` and `ipxe-option-space.conf` found in the 
    `/etc/dhcp/` folder
  * Start and enable the dhcpd service

## Requirements

The role requires a pre-installed version of the RHEL OS on the Autodeploynode.

## Role Variables

The variables for this role are located in the `dhcp-server/vars/main.yml` and 
`dhcp-server/defaults/main.yml`. These variables can be edited as needed.

## Dependencies

The role depends on the requirements listed above.

## Playbook

The role is called in the `dcaf/modules/autodeploynode/autodeploy.yml` playbook.
