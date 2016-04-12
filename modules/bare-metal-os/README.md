# CSC DCAF Bare Metal OS Deployment Automation

The Bare-Metal_OS module is an automated deployment of an operating system on
bare-metal hardware using Hanlon, currently the Red Hat Enterprise Linux OS. Though
it is an automated process there are a few things tha need to be in place before
you begin.

## Before You Begin

* Create the /opt/autodeploy/projects/inventory/hosts.ini file to include each
  host being deployed to.
* Create the /opt/autodeploy/projects/inventory/host_vars/host_name.yml file for 
  each host being deployed to.
* Create the /opt/autodeploy/projects/inventory/group_vars/bare-metal-os.yml file
  with the appropriate values for the deployment.
  
Refer to the CSC DCAF Documentation for more details and what is included in these
files.

## Run the Bare-Metal_OS Automation

Now that the inventory and variables have been created the automation can be used.

* Run the site_reset.yml playbook to ensure the hosts are discovered and ready for
  deployment.
* Run the site_deploy.yml playbook to deploy the RHEL OS.
