#!/usr/bin/python
import requests
DOCUMENTATION = '''
---
module: hanlon_model
short_description: Add a new model to Hanlon
description:
    - A Hanlon model describes how a bare metal server operating system should be configured when provisioning
    this module adds a model to Hanlon.
version_added: 2.0
author: Joseph Callen
requirements:
    - requests
    - Hanlon server
options:
    base_url:
        description:
            - The url to the Hanlon RESTful base endpoint
        required: true
    template:
        description:
            - The available OS templates for use with Hanlon.  From the CLI ./hanlon model templates
        required: true
    label:
        description:
            - Name of the model
        required: true
notes:
    - This module should run from a system that can access Hanlon directly. Either by using local_action, or using delegate_to.
    - The options for this module are dynamic based on the template type.  The req_metadata_hash and opt_metadata_hash keys map to options
'''
EXAMPLES = '''
- name: Add a RHEL image to Hanlon
  hanlon_image:
    base_url: "http://10.10.10.10:8026/hanlon/api/v1"
    type: os
    path: "/home/hanlon/image/rhel-server-7.2-x86_64-dvd-hnl.iso"
    name: rhel
    version: 7.2
    state: present
  register: rhel_image

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
'''

class HanlonModel(object):

    def __init__(self, module, metadata_hash):
        self.module = module
        self.metadata_hash = metadata_hash

        hanlon_model_states = {
            'absent': {
                'absent': self.state_exit_unchanged,
                'present': self.state_destroy_model
            },
            'present': {
                'absent': self.state_create_model,
                'present': self.state_exit_unchanged
            }
        }
        model_state, uuid = self.check_model_state()
        module.params['uuid'] = uuid
        hanlon_model_states[self.module.params['state']][model_state]()

    def create_new_hanlon_model(self):
        """
        This function creates the body of the POST request to the Hanlon server creating the model via the
        parameters provided by the AnsibleModule
        """

        req_metadata_params = dict()

        base_url = self.module.params['base_url']
        url = "%s/model" % base_url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        # We need to generate the req_metadata_params to POST into Hanlon
        for metadata in self.metadata_hash:
            # Because we have optional metadata we only want to include params
            # that have values assigned
            if metadata in self.module.params:
                if self.module.params[metadata]:
                    if len(self.module.params[metadata]) != 0:
                        req_metadata_params.update({metadata: self.module.params[metadata]})

        payload = {
            'label': self.module.params['label'],
            'template': self.module.params['template'],
            'req_metadata_params': req_metadata_params
        }

        # If we are using the boot_local and discover_only models
        # we do not want the image_uuid as its not required.
        # All other models it is required
        if (self.module.params['template'] != 'boot_local') or (self.module.params['template'] != 'discover_only'):
            payload.update({'image_uuid': self.module.params['image_uuid']})

        try:
            req = requests.post(url, data=json.dumps(payload), headers=headers)
            json_result = req.json()
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

        return json_result

    def check_model_state(self):
        base_url = self.module.params['base_url']
        model_name = self.module.params['label']

        uri = "%s/model" % base_url
        try:
            json_result, http_success = hanlon_get_request(uri)

            for response in json_result['response']:
                uri = response['@uri']
                model, http_success = hanlon_get_request(uri)
                if http_success:
                    model_response = model['response']
                    if model_response['@label'] == model_name:
                        return 'present', model_response['@uuid']
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

        return 'absent', None

    def state_exit_unchanged(self):
        uuid = self.module.params['uuid']
        self.module.exit_json(changed=False, uuid=uuid)

    def state_destroy_model(self):
        base_url = self.module.params['base_url']
        uuid = self.module.params['uuid']

        uri = "%s/model/%s" % (base_url, uuid)

        try:
            req = requests.delete(uri)
            if req.status_code == 200:
                self.module.exit_json(changed=True)
        except requests.ConnectionError as connect_error:
            self.module.fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
        except requests.Timeout as timeout_error:
            self.module.fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
        except requests.RequestException as request_exception:
            self.module.fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

        self.module.exit_json(changed=False)

    def state_create_model(self):
        new_model = self.create_new_hanlon_model()
        uuid = new_model['response']['@uuid']
        self.module.exit_json(changed=True, uuid=uuid)


def _jsonify(data):
    """
    Since I am doing things a little different as certain points in code execution I cannot use
    the provided AnsibleModule methods.  Instead I am modifying for specific use.
    https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/basic.py
    """
    for encoding in ("utf-8", "latin-1", "unicode_escape"):
        try:
            return json.dumps(data, encoding=encoding)
        # Old systems using simplejson module does not support encoding keyword.
        except TypeError, e:
            return json.dumps(data)
        except UnicodeDecodeError, e:
            continue
    _fail_json(msg='Invalid unicode encoding encountered')


def _fail_json(**kwargs):
    kwargs['failed'] = True
    print _jsonify(kwargs)
    sys.exit(1)


def peek_params(module_args):
    # if module_args starts with a {
    # then we know we are dealing with JSON
    # since we don't really care about unicode
    # in the Ansible basic.py lets just
    # convert it to a dictionary

    if module_args.startswith('{'):
        params = json.loads(module_args)
        return params['base_url'], params['template']
    else:
        base_url = ""
        template = ""
        items = shlex.split(module_args)
        for x in items:
            try:
                (k, v) = x.split("=", 1)
                if k == 'base_url':
                    base_url = v
                elif k == 'template':
                    template = v
            except Exception:
                _fail_json(msg="this module requires key=value arguments (%s)" % items)

        if len(base_url) == 0:
            _fail_json(msg="missing base_url argument")
        if len(template) == 0:
            _fail_json(msg="missing template argument")

        return base_url, template


def create_argument_spec(base_url, model_template):
    # Hanlon has two types of metadata: required and optional
    metadata_types = "@req_metadata_hash", "@opt_metadata_hash"
    metadata_hash = []
    argument_spec = dict()

    # Each OS template is defined, lets GET the current model template that we are working with
    url = "%s/model/templates/%s" % (base_url, model_template)

    # There is no image when we are using boot_local or discover_only models
    if (model_template == 'boot_local') or (model_template == 'discover_only'):
        argument_spec.update(image_uuid=dict(required=False))
    else:
        argument_spec.update(image_uuid=dict(required=True))

    argument_spec.update(
        base_url=dict(required=True),
        template=dict(required=True),
        label=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'], type='str')
    )

    try:
        req = requests.get(url)
        if req.status_code != 200:
            _fail_json(msg=req.text)

        template = req.json()
    except requests.ConnectionError as connect_error:
        _fail_json(msg="Connection Error; confirm Hanlon base_url.", apierror=str(connect_error))
    except requests.Timeout as timeout_error:
        _fail_json(msg="Timeout Error; confirm status of Hanlon server", apierror=str(timeout_error))
    except requests.RequestException as request_exception:
        _fail_json(msg="Unknown Request library failure", apierror=str(request_exception))

    try:
        for md_type in metadata_types:
            for metadata in template['response'][md_type]:
                # When we generate the req_metadata_params I will only want module.params key values
                # from the metadata.
                metadata_hash.append(metadata[1:])
                argument_spec.update({
                    metadata[1:]: dict(
                        {'required': template['response'][md_type][metadata]['required']}
                    )})
    except Exception as e:
        _fail_json(msg=e.message)

    return argument_spec, metadata_hash


def hanlon_get_request(uri):
    req = requests.get(uri)
    if req.status_code == 200:
        json_result = req.json()
        return json_result, True
    else:
        return None, False 


def main():

    # If ANSIBLE_VERSION is not defined we know that
    # we are using 2.1 and greater.  At least we hope so
    if 'ANSIBLE_VERSION' in globals():
        if int(ANSIBLE_VERSION[0]) < 2:
            module_args = MODULE_ARGS
        else:
            module_args = MODULE_COMPLEX_ARGS

        (base_url, model_template) = peek_params(module_args)
    else:
        module_args = _load_params()
        base_url = module_args['base_url']
        model_template = module_args['template']

    argument_spec, metadata_hash = create_argument_spec(base_url, model_template)
    module = AnsibleModule(argument_spec=argument_spec)

    HanlonModel(module, metadata_hash)

# If you are using this module with Ansible 2.1 _load_params
# also needs to be imported.  This function also does not 
# exist in earlier versions on basic.py so if it fails
# to load just ignore it.
try:
    from ansible.module_utils.basic import _load_params
except ImportError:
    pass

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
