#!/usr/bin/python
import requests

DOCUMENTATION = '''
---
module: hanlon_active_model
short_description: Get the current status of the active_model associated with
description:
    - A Hanlon model describes how a bare metal server operating system should be configured when provisioning
    this module adds a model to Hanlon.
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
'''

EXAMPLES = '''
- name: Wait for nodes to start installation
  local_action:
    module: hanlon_active_model
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    smbios_uuid: "{{ smbios_uuid }}"
  register: active_model
  until: not(active_model.current_state is none)
  retries: 20
  delay: 30

- name: Remove current Active Model for node
  local_action:
    module: hanlon_active_model
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    smbios_uuid: "{{ smbios_uuid }}"
    state: absent
'''

class HanlonActiveModel(object):

    def __init__(self, module):
        self.uuid = ""
        self.current_state = ""
        self.node_ip = ""
        self.model_label = ""
        self.base_url = module.params['base_url']
        self.smbios_uuid = module.params['smbios_uuid']
        self.module = module

        hanlon_active_model_states = {
            'absent': {
                'absent': self.state_exit_unchanged,
                'present': self.state_destroy_active_model
            },
            'present': {
                'absent': self.state_exit_unchanged,
                'present': self.state_exit_unchanged
            }
        }
        
        current_state = self.check_active_model_state()
        hanlon_active_model_states[self.module.params['state']][current_state]()

    def state_destroy_active_model(self):
        uri = "%s/active_model/%s" % (self.base_url, self.uuid)
    
        try:
            if not self.module.check_mode:
                req = requests.delete(uri)
                if req.status_code == 200:
                    self.module.exit_json(changed=True)
                else:
                    self.module.fail_json(msg="Unknown error", apierror=req.text)
            self.module.exit_json(changed=True)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

    def check_active_model_state(self):
        url = "%s/active_model?hw_id=%s" % (self.base_url, self.smbios_uuid)
    
        try:
            req = requests.get(url)
            if req.status_code == 200:
                active_model = req.json()
                if 'response' in active_model:
                    if '@model' in active_model['response']:
                        if '@label' in active_model['response']['@model']:
                            self.model_label = active_model['response']['@model']['@label']
                        else:
                            self.model_label = ""
                        if '@current_state' in active_model['response']['@model']:
                            self.current_state = active_model['response']['@model']['@current_state']
                        else:
                            self.current_state = ""
                        if '@node_ip' in active_model['response']['@model']:
                            self.node_ip = active_model['response']['@model']['@node_ip']
                        else:
                            self.node_ip = ""

                        self.uuid = active_model['response']['@uuid']

                        return 'present'
            elif req.status_code == 400:
                self.uuid = None
                self.current_state = None
                self.node_ip = None
                self.model_label = None
                return 'absent'
            else:
                self.module.fail_json(msg="Unknown error", apierror=req.text)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

    def state_exit_unchanged(self):
        self.module.exit_json(changed=False,
                              current_state=self.current_state,
                              node_ip=self.node_ip,
                              uuid=self.uuid,
                              model_label=self.model_label
                              )
    

def create_argument_spec():
    argument_spec = dict()

    argument_spec.update(
        base_url=dict(required=True),
        smbios_uuid=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'], type='str')
    )
    return argument_spec


def main():
    argument_spec = create_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    HanlonActiveModel(module)

    
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
