# CSC DCAF AutoDeployNode Deployment Automation

The **AutoDeployNode** is the main component of CSC DCAF automation. Once staged
it contains all the source files and dependencies needed to support the operation
of the automation framework to:

* **Discover** new nodes that are added to the pod. This process of automated
  discovery is driven by the Hanlon instance that is running on the AutoDeployNode
  (and a default, discover-only policy that has been added to that Hanlon instance).
* **Provision** new operating systems or hypervisors to those nodes. This process
  of policy-based provisioning is driven using Ansible and Hanlon, with Ansible
  creating the policies necessary to provision the right OS/hypervisor to the right
  node at the right time.
* **Deploy** new platforms into the OS/hypervisor instances that were provisioned
  to those nodes. The process of platform deployment is driven using Ansible.
* **Configure** the infrastructure associated with the pod, the nodes in the pod,
  and the platforms deployed to those nodes. The process of configuration at the
  infrastructure, OS/hypervisor, and platform layer is driven using Ansible.

As detailed in the documentation, the build of the AutoDeployNode is automated
through scripts and Ansible playbooks.

The AutoDeployNode can be deployed as a virtual machine or on physical hardware
with Red Hat Enterprise Linux as the base operating system. Docker containers are
used to stand up the Hanlon instance and it's requirements, MongoDB and a TFTP
server. In order to automatically discover and provision physical hardware, a DHCP
server is configured to provide addresses on the local subnet. Ansible is used as
the automation tool to deploy and configure systems and applications.
