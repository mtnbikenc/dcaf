#!/usr/bin/python
import requests
import urllib

DOCUMENTATION = '''
---
module: hanlon_node
short_description: Change the current power state of a node
description:
    - This module checks the current power state of a node and allows it to be changed.
version_added: null
author: Joseph Callen
requirements:
    - requests
    - Hanlon server
options:
    base_url:
        description:
            - The url to the Hanlon RESTful base endpoint
        required: true
        default: null
        aliases: []
    smbios_uuid:
        description:
            - The UUID or hardware ID from the system BIOS
        required: true
        default: null
        aliases: []
    power_command:
        description:
            - The current power state of the node
        required: true
    ipmi_username:
        description:
            - The user credential used for ipmi commands
        required: true
    ipmi_password:
        description:
            - The password credential used for ipmi commands
    ipmi_options:
        description:
            - JSON string for IPMI options
'''

EXAMPLES = '''
- name: Initiate reboot of node
  local_action:
    module: hanlon_node
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    smbios_uuid: "{{ smbios_uuid }}"
    username: root
    password: calvin
    power_state: "reset"
    ipmi_options: '{"driver": "lan20"}'
  register: node_reboot
  until: node_reboot.changed | default(false)
'''

class HanlonNode(object):
    def __init__(self, module):
        self.module = module
        self.check_node_power_state()

    def change_power_state(self, current_state):
        base_url = self.module.params['base_url']
        url = "%s/node/power" % (base_url)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
        if self.module.params['power_state'] == 'reset':
            if current_state == 'on':
                power_command = 'reset'
            else:
                power_command = 'on'
        else:
            power_command = self.module.params['power_state']
    
        payload = {
               'hw_id': self.module.params['smbios_uuid'],
               'power_command': power_command,
               'ipmi_username': self.module.params['username'],
               'ipmi_password': self.module.params['password'],
        }
    
        if self.module.params['ipmi_options'] is not None:
            payload.update({'ipmi_options': str(self.module.params['ipmi_options'])})
    
        try:
            if not self.module.check_mode:
                req = requests.post(url, data=json.dumps(payload), headers=headers)
                if req.status_code == 201:
                    req.json()
                    self.module.exit_json(changed=True)
                else:
                    self.module.fail_json(msg="Unknown Hanlon API error", apierror=req.text)
            self.module.exit_json(changed=True, uuid=None)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))
    
    def check_node_power_state(self):
    
        base_url = self.module.params['base_url']
        smbios_uuid = self.module.params['smbios_uuid']
        power_state = self.module.params['power_state']
        username = self.module.params['username']
        password = self.module.params['password']
    
        if self.module.params['ipmi_options'] is not None:
            ipmi_options = urllib.quote(str(self.module.params['ipmi_options']))
            url = "%s/node/power?hw_id=%s&ipmi_username=%s&ipmi_password=%s&ipmi_options=%s" % (base_url, smbios_uuid, username, password, ipmi_options)
        else:
            url = "%s/node/power?hw_id=%s&ipmi_username=%s&ipmi_password=%s" % (base_url, smbios_uuid, username, password)
    
        try:
            req = requests.get(url)
            if req.status_code == 200:
                active_model = req.json()
                if 'response' in active_model:
                    if 'Status' in active_model['response']:
                        current_state = active_model['response']['Status']
                        if current_state == power_state:
                            self.module.exit_json(changed=False)
                        else:
                            self.change_power_state(current_state)
    
            else:
                self.module.fail_json(msg="Unknown error", apierror=req.text)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))


def create_argument_spec():
    argument_spec = dict()

    argument_spec.update(
        base_url=dict(required=True),
        smbios_uuid=dict(required=True),
        username=dict(required=True, type='str'),
        password=dict(required=True, type='str', no_log=True),
        power_state=dict(required=True, choices=['on', 'off', 'reset'], type='str'),
        ipmi_options=dict(required=False, type='str')
    )
    return argument_spec


def main():
    argument_spec = create_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    HanlonNode(module)
    

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
