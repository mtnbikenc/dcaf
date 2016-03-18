#!/usr/bin/python

__author__ = 'jcallen'


try:
    import json
except ImportError:
    import simplejson as json


from subprocess import Popen, PIPE
import sys
import re

from ansible.module_utils.basic import *


def generic_ipmitool_power_operation(module, desired_power_state):
    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']

    cmd_line = "ipmitool -I lanplus -H %s -U %s -P %s power %s" % (hostname, username, password, desired_power_state)
    output, err, return_code = execute_process(cmd_line)

    if return_code == 0:
        return True
    else:
        module.fail_json(msg=err)


def ipmitool_power_on(module):
    current_state = get_current_state(module)
    if current_state == "off":
        generic_ipmitool_power_operation(module, "on")
        return True
    else:
        return False

def ipmitool_power_off(module):
    current_state = get_current_state(module)
    if current_state == "on":
        generic_ipmitool_power_operation(module, "off")
        return True
    else:
        return False

def ipmitool_power_reset(module):
    current_state = get_current_state(module)
    if current_state == "on":
        generic_ipmitool_power_operation(module, "reset")
        return True
    elif current_state == "off":
        generic_ipmitool_power_operation(module, "on")
        return True
    else:
        return False


def get_current_state(module):
    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']

    cmd_line = "ipmitool -I lanplus -H %s -U %s -P %s power status" % (hostname, username, password)
    output, err, return_code = execute_process(cmd_line)

    if return_code == 0:
        if "off" in output:
            return "off"
        elif "on" in output:
            return "on"
        else:
            return "unknown"
    else:
        module.fail_json(msg=err)


'''
Executes process using the shell, waits for the command to exit and
returns returns output (string), err (string), return_code (int)
'''


def execute_process(cmd_line):
    try:
        process = Popen(cmd_line, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = process.communicate()
        return_code = process.returncode
        return output, err, return_code
    except Exception as e:
        syslog.syslog("Exception %s in execute_process()" % str(e))
        sys.exit(1)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            power_state=dict(required=True, choices=['on', 'off', 'reset'], type='str'),
            ),
        supports_check_mode=False
    )

    # This is the defines our desired state which will be
    # returned from the playbook
    desired_power_state = module.params['power_state']

    power_states = {
        "on": ipmitool_power_on,
        "off": ipmitool_power_off,
        "reset": ipmitool_power_reset,
        }

    changed = power_states[desired_power_state](module)

    # changed = ipmitool_power_ops(module)
    module.exit_json(changed=changed)

if __name__ == '__main__':
    main()
