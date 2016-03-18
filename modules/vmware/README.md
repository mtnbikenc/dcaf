# CSC DCAF VMware Infrastructure Deployment Automation

This project contains the Ansible playbooks and roles to deploy the bare-metal
installation of VMware vSphere 5.5.

## Requirements
CSC DCAF has only been tested on Red Hat derivative distributions.  We suggest
to use the latest version of CentOS with EPEL repo added.

- [Hanlon](https://github.com/csc/Hanlon)
- [Ansible 2.0](https://github.com/ansible/ansible)
- [OVF Tool](https://www.vmware.com/support/developer/ovf/)
- [vSphere CLI](https://developercenter.vmware.com/tool/vsphere_cli/6.0)

## Inventory
The project inventory must be modified for your deployment environment. The
specific files that need to modified are listed below.

### group_vars

#### foundation_esxi.yml

Below is an example of `foundation_esxi.yml`.  The VLAN IDs and the IPMI values
should be the only modifications necessary.

```yaml
---
ansible_ssh_user: root
ansible_ssh_pass: "{{ site_passwd }}"
mgmt_vlan_id: 1801
vmotion_vlan_id: 1802
vsan_vlan_id: 1803
ipmi_username: root
ipmi_password: calvin
```

#### all common.yml

The variables in the `common.yml` needs to be reviewed and modified as necessary.
Do not modify the hanlon_base_url unless you know what you are doing.

```yaml
---
# These are development IP addresses and need to be changed
auto_deploy_node: 172.17.16.10
domain_name: lordbusiness.local
dns_servers: 192.168.70.3,192.168.70.4
dns_server: 192.168.70.3
ntp_servers: 172.17.16.10
pxe_subnet_mask: 255.255.255.0
# Hanlon vars
hanlon_base_url: http://{{ auto_deploy_node }}:8026/hanlon/api/v1/
esxi_iso_path: /home/hanlon/image/VMware-VMvisor-Installer-201501001-2403361.x86_64.iso
esxi_image_name: VMware_ESXi
esxi_version: 5.5
# ESXi license must be valid or deployment will fail
# esx_license was moved into all/secrets.yml (expires 9/14/2015)
#esx_license:
esxi_username: root
mgmt_vdc: Test-Lab
mgmt_cluster: Foundation
mgmt_vmk: vmk1
mgmt_subnet_mask: 255.255.255.0
vmotion_vmk: vmk2
vmotion_subnet_mask: 255.255.255.0
vsan_vmk: vmk3
vsan_subnet_mask: 255.255.255.0
dvs_vmnic: vmnic5
vss_vmnic: vmnic4
```

#### all secrets.yml

We currently store variables `site_passwd` and `esx_license` in `secrets.yml`.
Information regarding Ansible Vault is available here:
http://docs.ansible.com/ansible/playbooks_vault.html

### host_vars

#### foundation-esxi-0x.yml

The individual host specific variables are listed in the
`/inventory/host_vars/foundation-esxi-0x.yml` files.  Every item of this file
must be modified for the IP addressing of your environment.  The `smbios_uuid`
is required for Hanlon to create policies associated with a specific node.

```yaml
---
hostname: cscesxtmp001
mgmt_ip_address: 172.17.17.15
vmotion_ip_address: 172.17.18.15
vsan_ip_address: 172.17.19.15
pxe_ip_address: 172.17.16.15
oob_ip_address: 172.30.0.77
smbios_uuid: 4C4C4544-005A-5210-8043-B8C04F443432
```

#### foundation-vcsa.yml

The final inventory file that needs to be modified is for the vCenter Appliance.
The `vcsa_ova` is the path to the OVA on the filesystem.

```yaml
---
ansible_ssh_user: root
ansible_ssh_pass: vmware
ansible_ssh_host: "{{ mgmt_ip_address }}"
hostname: cscvcatmp001
mgmt_ip_address: 172.17.17.18
mgmt_subnet_mask: 255.255.255.0
mgmt_gateway: 172.17.17.1
vcsa_ova: /opt/deploy/VMware-vCenter-Server-Appliance-5.5.0.20000-2063318_OVF10.ova
vcsa_user: root
vcsa_pass: vmware
```

## Execution

Execute this module by running:

    ansible-playbook site.yml

### YouTube Video
[![Ansible vSphere Deployment](http://img.youtube.com/vi/H1XYuOodiak/0.jpg)](http://www.youtube.com/watch?v=H1XYuOodiak)
