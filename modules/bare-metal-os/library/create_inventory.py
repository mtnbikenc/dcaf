#!/usr/bin/python

DOCUMENTATION = '''
---
module: create_inventory
short_description: Create Ansible Inventory from CSV file
description:
    - This module will take a CSV input file and create the inventory/host_vars
    files and inventory/hosts.ini file for the CSC DCAF bare-metal-os module.
version_added: null
author: Russell Teague
requirements:
    - Properly formatted CSV file
options:
    file:
        description:
            - The input inventory CSV file
        required: true
        default: null
    path:
        description:
            - The destination inventory directory path
        required: true
        default: null
'''

EXAMPLES = '''
Example from Ansible playbook
    - name: Create Ansible inventory from CSV file
      local_action:
        module: create_inventory
        file: example_inventory.csv
        path: ./inventory/
'''


import csv
import yaml
import ConfigParser


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def main():

    argument_spec = dict(
        file=dict(required=True, type='str'),
        path=dict(required=True, type='str'))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False)

    input_file = module.params['file']
    dest_folder = module.params['path']

    # Make sure the destination folder exists
    mkdir_p(dest_folder + '/host_vars')

    # Initialize the hosts.ini configuration
    hosts_ini = ConfigParser.RawConfigParser(allow_no_value=True)

    # Read the inventory CSV file
    input_dict = {}
    try:
        input_dict = csv.DictReader(open(input_file))
    except Exception as e:
        module.fail_json(msg=str(e))

    # Process each row to create the host_vars/hostname.yml files
    update_list = []
    for row in input_dict:
        # We need to update the hosts.ini here with the hostname based on groups
        # Split the 'groups' if necessary
        for item in row['groups'].split(','):
            if not hosts_ini.has_section(item):
                hosts_ini.add_section(item)
            hosts_ini.set(item, row['hostname'])

        # Remove 'groups' as we don't want it in the host_vars file
        del row['groups']

        # Retrieve the hostname and remove it from the dictionary
        host_var_filename = row.pop('hostname') + ".yml"

        # Remove empty values because we don't want them to override group_vars
        empty_keys = dict((k, v) for k, v in row.iteritems() if v is '')
        for k in empty_keys:
            del row[k]

        # Make a copy of the row before we start to iterate and make changes
        new_row = row.copy()

        # Create the default items in host_vars files
        new_row['ansible_ssh_host'] = new_row['pxe_ip_address']

        for k, v in row.iteritems():
            # Create sub-dictionaries from 'dotted' keys
            if '.' in k:
                # Delete the key from 'row'
                del new_row[k]
                # Split the key into two parts
                new_d, new_k = k.split('.', 1)
                if new_d not in new_row:
                    new_row[new_d] = {}
                new_row[new_d][new_k] = v
            # Create lists for comma separated values
            elif (v is not None) and (',' in v):
                v_list = v.split(",")
                new_row[k] = v_list

        # Write out host_var file for each node
        try:
            with open(dest_folder + "/host_vars/" + host_var_filename, 'w') \
                    as f:
                yaml.safe_dump(new_row, f,
                               default_flow_style=False,
                               explicit_start=True)
                update_list.extend([f.name])
        except Exception as e:
            module.fail_json(msg=str(e))

    # Create the autodeploynode.yml host_vars file
    deploy_node_host_var = {'ansible_ssh_host': '{{ autodeploynode }}'}
    try:
        with open(dest_folder + "/host_vars/autodeploynode.yml", 'w') as f:
            yaml.safe_dump(deploy_node_host_var, f,
                           default_flow_style=False,
                           explicit_start=True)
            update_list.extend([f.name])
    except Exception as e:
        module.fail_json(msg=str(e))

    # Add the default sections to hosts.ini
    hosts_ini.add_section('autodeploynode')
    hosts_ini.set('autodeploynode', 'autodeploynode')

    hosts_ini.add_section('mongodb:children')
    hosts_ini.set('mongodb:children', 'controller')

    hosts_ini.add_section('openstack:children')
    hosts_ini.set('openstack:children', 'controller')
    hosts_ini.set('openstack:children', 'compute')
    hosts_ini.set('openstack:children', 'swift')

    hosts_ini.add_section('deploy:children')
    hosts_ini.set('deploy:children', 'openstack')
    hosts_ini.set('deploy:children', 'scaleio')

    hosts_ini.add_section('sds:children')
    hosts_ini.set('sds:children', 'mdm')
    hosts_ini.set('sds:children', 'tb')

    hosts_ini.add_section('gateway:children')
    hosts_ini.set('gateway:children', 'controller')

    hosts_ini.add_section('sdc:children')
    hosts_ini.set('sdc:children', 'sds')
    hosts_ini.set('sdc:children', 'gateway')
    hosts_ini.set('sdc:children', 'compute')

    # Write the hosts.ini
    try:
        with open(dest_folder + '/hosts.ini', 'wb') as f:
            hosts_ini.write(f)
            update_list.extend([f.name])
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=True, update_list=update_list)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
