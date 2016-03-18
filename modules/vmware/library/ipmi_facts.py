#!/usr/bin/python

import re


def ipmitool_get_uuid(module):
    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']

    cmd = "ipmitool -I lanplus -H %s -U %s -P %s bmc guid" % (hostname, username, password)
    rc, stdout, stderr = module.run_command(cmd)

    if rc == 0:
        match = re.findall("System GUID[ ]+:[ ]([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})", stdout)
        if len(match) >= 1:
            module.exit_json(changed=False, smbios_uuid=match[0])
        else:
            module.fail_json(msg="No SMBIOS UUID available")
    else:
        module.fail_json(msg=err)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, aliases=['name', 'host'], type='str'),
            username=dict(required=True, aliases=['user', 'admin'], type='str'),
            password=dict(required=True, aliases=['pass', 'pwd'], type='str'),
            ),
        supports_check_mode=False
    )

    ipmitool_get_uuid(module)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
