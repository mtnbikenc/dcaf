#!/usr/bin/python
import requests

DOCUMENTATION = '''
---
# If a key doesn't apply to your module (ex: choices, default, or
# aliases) you can use the word 'null', or an empty list, [], where
# appropriate.
module: hanlon_policy
short_description: Add a new policy to Hanlon
description:
    - A Hanlon policy describes the rules for binding a node to operating system model.
version_added: null
author: Joseph Callen, Russell Teague
notes: null
requirements:
    - Hanlon server
options:
    base_url:
        description:
            - The url to the Hanlon RESTful base endpoint
        required: true
        default: null
        aliases: []
    template:
        description:
            - The available policy templates for use with Hanlon.  From the CLI ./hanlon policy templates
        required: true
        default: null
        aliases: []
    label:
        description:
            - The name of the policy
        required: true
        default: null
        aliases: []
    model_uuid:
        description:
            - The model UUID to use for this policy
        required: true
        default: null
        aliases: []
    tags:
        description:
            - The tags which should match the node for binding
        required: true
        default: null
        aliases: []
    enabled:
        description:
            - The state of the policy
        required: false
        default: true
        aliases: []
    line_number:
        description:
            - The line number in the policy table the policy should exist
        required: false
        default: null
        aliases: []
    is_default:
        description:
            - Set policy as system default
        required: false
        default: null
        aliases: []
notes:
    - This module should run from a system that can access Hanlon directly. Either by using local_action, or using delegate_to.
'''
EXAMPLES = '''
- name: Add a RHEL Model to Hanlon
  hanlon_model:
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    template: redhat_7
    label: "RHEL7"
    image_uuid: "{{ rhel_image.uuid }}"
    hostname_prefix: localhost
    domainname: localdomain.local
    root_password: test1234
    partition_scheme: |
      part /boot --ondisk=sda --size=512  --fstype=ext3
      part swap  --ondisk=sda --size=4096 --fstype=swap
      part pv.01 --ondisk=sda --size=1 --grow
      volgroup vg_root pv.01
      logvol / --vgname=vg_root --size=32768 --name=lv_root --fstype=xfs --grow
      ignoredisk --only-use=sda
    state: present
  register: rhel_model

- name: Create policy for node using SMBIOS UUID
  hanlon_policy:
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    policy_template: linux_deploy
    label: rhel7_policy
    model_uuid: "{{ rhel_model.uuid }}"
    tags: "{{ hostvars[item].smbios_uuid }}"
    enabled: true
    state: present
  with_items: groups['deploy']
'''


class HanlonPolicy(object):
    def __init__(self, module):
        self.module = module
        hanlon_policy_states = {
            'absent': {
                'absent': self.state_exit_unchanged,
                'present': self.state_destroy_policy
            },
            'present': {
                'absent': self.state_create_policy,
                'present': self.state_exit_unchanged,
                'update': self.state_update_policy
            }
        }
        policy_state = self.check_policy_state()

        hanlon_policy_states[self.module.params['state']][policy_state]()
        
    def state_create_policy(self):
        base_url = self.module.params['base_url']
        url = "%s/policy" % base_url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
        payload = {
            'template':   self.module.params['policy_template'],
            'label':      self.module.params['label'],
            'model_uuid': self.module.params['model_uuid'],
        }
    
        if None in payload.values():
            self.module.fail_json(msg="Missing required arguments for creating a new policy.")
    
        if self.module.params['enabled'] is not None:
            payload.update({
                'enabled': self.module.params['enabled']
            })
        if self.module.params['is_default'] is not None:
            payload.update({
                'is_default': self.module.params['is_default']
            })
        if self.module.params['tags'] is not None:
            payload.update({
                'tags': self.module.params['tags']
            })
        if self.module.params['maximum'] is not None:
            payload.update({
                'maximum': str(self.module.params['maximum'])
            })
        if self.module.params['line_number'] is not None:
            payload.update({'line_number': str(self.module.params['line_number'])})
    
        try:
            if not self.module.check_mode:
                req = requests.post(url, data=json.dumps(payload), headers=headers)
                if req.status_code == 201:
                    json_result = req.json()
                    uuid = json_result['response']['@uuid']
                    self.module.exit_json(changed=True, uuid=uuid)
                else:
                    self.module.fail_json(msg="Unknown Hanlon API error", apierror=req.text)
            self.module.exit_json(changed=True, uuid=None)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))
    
    def hanlon_get_request(self, uri):
        req = requests.get(uri)
        if req.status_code == 200:
            json_result = req.json()
            return json_result, True
        else:
            return None, False
    
    def check_diff(self, policy_response):
        policy_name = self.module.params['label']
        if policy_response['@label'] == policy_name:
            self.module.params['uuid'] = policy_response['@uuid']
    
            # The Hanlon API is a little screwy with tags
            # the PUT/POST wants a comma delimited string
            # the JSON result from a Policy query is an array/list of
            # strings, adding to a complication when comparing.
            # Along with the fact that the return type of integers
            # is actually a string.
    
            if self.module.params['enabled'] is not None:
                if self.module.params['enabled'] != policy_response['@enabled']:
                    return 'update'
            if self.module.params['line_number'] is not None:
                if str(self.module.params['line_number']) != str(policy_response['@line_number']):
                    return 'update'
            if self.module.params['tags'] is not None:
                tags = self.module.params['tags'].split(",")
                if tags != policy_response['@tags']:
                    return 'update'
            if self.module.params['maximum'] is not None:
                if str(self.module.params['maximum']) != str(policy_response['@maximum_count']):
                    return 'update'
            return 'present'
        else:
            return 'absent'
    
    def check_policy_state(self):
        base_url = self.module.params['base_url']
        uri = "%s/policy" % base_url
        self.module.params['uuid'] = None
        state = 'absent'
        
        try:
            json_result, http_success = self.hanlon_get_request(uri)
    
            for response in json_result['response']:
                uri = response['@uri']
    
                # if this is run in a play concurrently with inventory
                # objects the uri may no longer exist if the
                # task is defined as state: absent.  If 
                # the result is not available skip it.
    
                policy, http_success = self.hanlon_get_request(uri)
                if http_success:
                    policy_response = policy['response']
                    state = self.check_diff(policy_response)
                    if state is not 'absent':
                        break
            return state
    
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))
    
    
    def state_update_policy(self):
        base_url = self.module.params['base_url']
        uuid = self.module.params['uuid']
        url = "%s/policy/%s" % (base_url, uuid)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
        payload = {'enabled': self.module.params['enabled']}
    
        if self.module.params['line_number'] is not None:
            payload.update({'new_line_number': str(self.module.params['line_number'])})
        if self.module.params['tags'] is not None:
            payload.update({'tags': self.module.params['tags']})
        if self.module.params['maximum'] is not None:
            payload.update({'maximum': str(self.module.params['maximum'])})
    
        try:
            if not self.module.check_mode:
                req = requests.put(url, data=json.dumps(payload), headers=headers)
                if req.status_code == 200:
                    self.module.exit_json(changed=True, uuid=uuid)
                else:
                    self.module.fail_json(msg="Unknown Hanlon API error", apierror=req.text)
            self.module.exit_json(changed=True, uuid=uuid)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))
    
    
    def state_exit_unchanged(self):
        uuid = self.module.params['uuid']
        self.module.exit_json(changed=False, uuid=uuid)
    
    
    def state_destroy_policy(self):
        base_url = self.module.params['base_url']
        uuid = self.module.params['uuid']
    
        uri = "%s/policy/%s" % (base_url, uuid)
    
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            base_url=dict(required=True, type='str'),
            policy_template=dict(required=False, type='str'),
            label=dict(required=True, type='str'),
            model_uuid=dict(required=False, type='str'),
            tags=dict(required=False, type='str'),
            enabled=dict(required=False, type='bool', default=True),
            line_number=dict(required=False, type='int'),
            is_default=dict(required=False, type='bool'),
            maximum=dict(required=False, type='int'),
            state=dict(required=False, default='present', choices=['present', 'absent'], type='str')
        ), supports_check_mode=True
    )
    HanlonPolicy(module)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
