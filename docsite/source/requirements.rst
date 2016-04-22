Requirements & Dependencies
===========================

A CSC DCAF Deployment has the following requirements and dependencies.

User Access Requirements
------------------------

To retrieve the automation resources from their online repositories you will
need the following:

- A valid github.com user account with access to the CSC Git repositories.
- A user account on the Red Hat website with a valid subscription associated
  with it.

Physical Hardware
-----------------

DCAF was developed and tested with the following hardware:

- DELL PowerEdge 630 | PowerEdge 730
- DELL PERC H730 RAID Controller

Network Requirements
--------------------

There are several network requirements for the deployment.

- DNS server IP addresses need to be provided
- NTP server IP address needs to be provided
- The following VLANS are required:

  - Out-of-band management (IPMI)
  - PXE Network

- Out-of-band Network IP address for each node
- Management IP address for each node

AutoDeployNode
--------------

The AutoDeployNode will contain all the necessary automation resources to use
CSC DCAF.

It has the following requirements:

- Deployed on a dedicated physical device with OOB management or a virtual
  machine in the environment
- Has an IP address on the PXE network
- At least 128GB HDD (SSD)
- Dual core CPU
- 16GB RAM

Target Deployment Environment
-----------------------------

The target deployment environment consists of all nodes that will participate in
the deployment.

- The physical hardware has been installed and connected to the network
- A 1GB connection for OOB management on the management switch
- 2 10GbE connections to the 10GbE network switches
- The upstream and management network have already been configured
- An on-site resource to configure the out-of-band management IP
  addresses
