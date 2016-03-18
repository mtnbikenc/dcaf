# CSC DCAF Bare Metal OS Deployment Automation

This project deploys RHEL 7 to bare metal nodes using Hanlon and Ansible.

* Create an inventory CSV file using inventory/example_inventory.csv as an
example
* Update inventory/group_vars/all.yml as needed
* Run ansible-playbook site_inventory.yml to create the Ansible Inventory
* Run ansible-playbook site_inventory.yml a second time to make sure the SMBIOS
UUIDs are updated in the host_vars files
* Run ansible-playbook site_reset.yml to ensure the hosts are discovered and
ready for deployment
* Run ansible-playbook site_deploy.yml to deploy RHEL
