#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys

DOCUMENTATION = '''
---
module: get_mac_if
author: Jeff Dexter (jdextercsc@users.noreply.github.com)
requirement:
short_description: This module take a provided MAC and returns the device that it is associated with.
options:
    mac:
        required: true
        default: None
        description: This is the hardware address that is being searched for.
'''

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False


class get_mac_if(object):
    platform = 'Generic'
    distribution = None

    def __init__(self, module):
        self.module = module
        self.mac = module.params['mac']
        self.device_name = ''

    def match_device(self):
        interfaces = netifaces.interfaces()
        for device in interfaces:
            addresses = netifaces.ifaddresses(device)
            link_addresses = addresses[netifaces.AF_LINK]
            for address in link_addresses:
                device_hwaddr = address['addr']
                if self.mac.lower() == device_hwaddr.lower():
                    self.device_name=device
                    return device
	return -1

def main():
    module = AnsibleModule(
        argument_spec=dict(
            mac=dict(default=None, required=True, type='str'),
        ),
        supports_check_mode=False
    )


    if not HAS_NETIFACES:
        module.fail_json(msg='python-netifaces is required for this module')

    Get_Mac_If = get_mac_if(module)

    rc=None
    out=''
    err=''
    result={}
    result['MAC']=Get_Mac_If.mac
    # check to see if interface is present
    if Get_Mac_If.match_device() != -1:
        result['if_device']=Get_Mac_If.device_name
    else:
        module.fail_json(changed=False, msg="Hardware address does not match any devices on system")


    module.exit_json(**result)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
