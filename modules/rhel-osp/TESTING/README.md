## OSP virtualized Testing environment for DCAF Project 
This project was created to build and prepare a virtualized environment for
testing the DCAF RHEL OSP automated installation.  This project includes two
main ansible playbooks, create.yml and delete.yml.

# Create
Create.yml does the following tasks:
- creates ansible network
- creates management network
- creates router
   - adds ansible and management network to router
   - sets gateway for router
- Deletes old stack if still here.
- Dynamically creates heat template
- creates heat stack
- sets up networking 

# Delete
Delete.yml does the following tasks:
- unregisters the VMs from RHN
- deletes the floatingIPs for later use.
- deletes the Heat stack.

The variables needed for using the testing enviromnment are all in the testing groupvar
../inventory/group_vars/testing.yml

 
