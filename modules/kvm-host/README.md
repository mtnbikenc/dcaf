# CSC DCAF KVM Host Automation Module


## Introduction:
This Module takes a RHEL 7 system and:

* Installs and configures libvirt, to provide KVM support.
 
* Creates bridges based off current networking and provides those bridges to libvirt for VM consumption.
   
    *This playbook assumes that all the base networking (ie vlans, bonds) have been previously configured.  Please see the bare-metal-os module for more information*
 
* Configures a template VM based off of a generic image, then clones that template to make `x` number of VMs on a specified KVM host.
 
## Usage

Update the inventory files, examples have been provided within `inventory`

* update `group_vars/kvm-hosts.yml` with your specific information.  Particularly:

<pre><code>
    #RHN credentials to register systems, Credentials can be added here or passed via the CLI
    rhn_user: 
    rhn_pass: 
    # Location and name of the qcow image to use as base
    qcow_image_name: /root/rhel-guest-image-7.1.qcow2
    
    # The following are defaulted within the role, change as needed.
    vm_root_password: redhat
    vm_ram: 16384
    vm_vcpus: 8
    
    # ansible_host_pubkey is the public key to be inserted into the VMs for passwordless ssh from the autodeploynode
    # this is the key found at /root/.ssh/id_rsa.pub or whatever is being used by ansible for access to hosts.
    ansible_host_pubkey:
    
    #MAC for the base nic on the template VM.
    basevm_mac: "52:54:00:FC:00:A0"
    #IP address for the base nic on the template VM. Be sure this is within the DHCP range on the AutoDeployNode.
    basevm_static_ip: 172.17.16.30
</code></pre>

* Update the `hosts.ini` file as seen in the example provided in the inventory.

* Update the `host_var/*` files based on the examples provided.

    *Note: the mgmt_ip, needs to be within the dhcp range on the AutoDeployNode*

* Run playbook by using running `site.yml`.  If something goes wrong during the kvm run, the KVM hosts can be reverted back to the orignal configuration using the `reset.yml` playbook.
