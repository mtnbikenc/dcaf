#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys

DOCUMENTATION = '''
---
module: iptables
author: jdextercsc
requirement: iptables-
short_description: appends iptables rules to a run time configuration and saves
the resulting iptables rule chain to disk
options:
    chain:
        required: false
        default: 'INPUT'
    protocol:
        required: false
        default: 'tcp'
        choices: ['tcp', 'udp', 'icmp', 'all']
    port:
        required: false
        description: a list of ports to open
    source:
        required: false
        description: Indicates the source for this the packet. This can be ip address, or network address, or
            hostname For example: 192.168.1.101 indicates a specific ip address. For network mask use /mask. For
            example: "192.168.1.0/24″ represents a network mask of 255.255.255.0 for that network.
            This matches 192.168.1.x network.
    dest:
        required: false
        description: Indicates the destination for this the packet. This can be ip address, or network address, or
            hostname For example: 192.168.1.101 indicates a specific ip address. For network mask use /mask. For
            example: "192.168.1.0/24″ represents a network mask of 255.255.255.0 for that network.
            This matches 192.168.1.x network.
    comment:
        required: false
        description: a string containing a descriptive comment about the rule.
    target:
        required: false
        description: a string containing the target for the iptables rule. Possible values are ACCEPT, DROP, QUEUE,
        RETURN, You can also specify other user defined chain as target value.
        default: ACCEPT
    match:
        required: false
        description:  Matching rule, example "--state ESTABLISHED,RELATED"
    # table:
    #     required: false
    #     description:  The table to apply the rule to.
    #     default: filter
    #     choices: ['filter', 'nat', 'mangle']
    in_interface:
        required: false
        description: the input interface
    out_interface:
        required: false
        description: the output interface
    state:
         required: false
         choices: ['absent', 'present']
         default: present
    position:
        required: false
        description:  use 'append' to add rule to end of chain, or an integer for the
            position to insert the rule at in the chane
        default: 'append'
'''


class Iptables(object):
    platform = 'Generic'
    distribution = None

    def __init__(self, module):
        self.module = module
        self.state = module.params['state']
        self.chain = module.params['chain']
        self.protocol = module.params['protocol']
        self.port = module.params['port']
        self.source = module.params['source']
        self.dest = module.params['dest']
        self.comment = module.params['comment']
        self.target = module.params['target']
        self.in_if = module.params['in_interface']
        self.out_if = module.params['out_interface']
        self.position = module.params['position']
        self.match = module.params['match']
        self.command = []
        self.command.append(self.build_chain())
        self.command.append(self.build_position())
        self.command.append(self.build_protocol())
        self.command.append(self.build_match())
        self.command.append(self.build_interfaces())
        self.command.append(self.build_source())
        self.command.append(self.build_dest())
        self.command.append(self.build_port())
        self.command.append(self.build_comment())
        self.command.append(self.build_target())

    def build_cmd(self, for_delete):
        cmd_string = ""
        if not for_delete:
            for parts in self.command[1:]:
                if parts is not None:
                    cmd_string += parts
        else:
            cmd_string += self.command[0]
            for parts in self.command[2:]:
                if parts is not None:
                    cmd_string += parts
        return cmd_string

    def build_port(self):
        cmd_string = ""
        if self.port is not None:
            if isinstance(self.port, list):
                ports = ",".join(map(str, self.port))
                cmd_string += " -m multiport --dport %s" % ports
            else:
                cmd_string += " --dport %s" % self.port
            return cmd_string

    def build_chain(self):
        cmd_string = ""
        if self.chain is None:
            cmd_string += "INPUT"
        else:
            cmd_string += " %s" % self.chain
        return cmd_string

    def build_match(self):
        cmd_string = ""
        if self.match is not None:
            self.command[2] = ''
            cmd_string += " -m %s" % self.match
            return cmd_string

    def build_position(self):
        cmd_string = ""
        chain_name = self.build_chain()
        if self.position is None or self.position is 'append':
            cmd_string += " -A %s" % chain_name
            return cmd_string
        elif isinstance(self.position, int):
            cmd_string += ' -I %s %d' % (chain_name, self.position)
            return cmd_string
        else:
            err = "position value %s, was not either 'append' or an integer"
            self.module.fail_json(msg=err)

    def build_source(self):
        cmd_string = ""
        if self.source is not None:
            cmd_string += " -s %s" % self.source
        return cmd_string

    def build_dest(self):
        cmd_string = ""
        if self.dest is not None:
            cmd_string += " -d %s" % self.dest
        return cmd_string

    def build_protocol(self):
        cmd_string = ""
        if self.protocol is None:
            cmd_string += " -p tcp"
        else:
            cmd_string += " -p %s" % self.protocol
        return cmd_string

    def build_comment(self):
        cmd_string = ""
        if self.comment is not None:
            cmd_string += ' -m comment --comment "%s"' % self.comment
        return cmd_string

    def build_interfaces(self):
        cmd_string = ""
        if self.in_if is not None or self.out_if is not None:
            if self.in_if is not None:
                cmd_string += ' -i %s' % self.in_if
            if self.out_if is not None:
                cmd_string += ' -o %s' % self.out_if
            return cmd_string

    def build_target(self):
        cmd_string = ""
        if self.target is None:
            cmd_string += ' -j ACCEPT'
        elif self.target is not None:
            cmd_string += ' -j %s' % self.target
        return cmd_string

    def check_rule(self):
        cmd_string = self.build_cmd(True)
        cmd = "iptables -vC %s" % cmd_string
        rc, out, err = self.module.run_command(cmd)
        exists = True
        if rc is 0:
            exists = False
        elif rc is 2:
            self.module.fail_json(msg=err)
        elif rc is 1 and self.module.check_mode:
            self.module.exit_json(changed=True)
        return exists

    def delete_rule(self):
        cmd_string = self.build_cmd(True)
        cmd = "iptables -v %s" % cmd_string
        rc, out, err = self.module.run_command(cmd)
        if rc is 1:
            self.module.fail_json(msg="failed to add rule %s with error %s" % (cmd_string, err))
        else:
            cmd = 'service iptables save'
            rc, out, err = self.module.run_command(cmd)
            if rc is 1:
                self.module.fail_json(msg=err)
            else:
                self.module.exit_json(changed=True, msg=cmd_string)

    def create_rule(self):
        cmd_string = self.build_cmd(False)
        cmd = "iptables -v %s" % cmd_string
        rc, out, err = self.module.run_command(cmd)
        if rc is 1:
            self.module.fail_json(msg="failed to add rule %s with error %s" % (cmd_string, err))
        else:
            cmd = 'service iptables save'
            rc, out, err = self.module.run_command(cmd)
            if rc is 1:
                self.module.fail_json(msg=err)
            else:
                self.module.exit_json(changed=True, msg=cmd_string)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            chain=dict(default='INPUT', required=False),
            protocol=dict(required=False, default='tcp', choices=['tcp', 'udp', 'icmp', 'all']),
            port=dict(required=False),
            source=dict(required=False),
            dest=dict(required=False),
            match=dict(required=False),
            comment=dict(required=False),
            target=dict(default="ACCEPT", required=False),
            in_interface=dict(required=False),
            out_interface=dict(required=False),
            state=dict(required=False, default='present', choices=['present', 'absent']),
            position=dict(required=False, default='append'),
        ),
        supports_check_mode=True
    )

    iptables = Iptables(module)

    if iptables.state == 'present':
        if iptables.check_rule():
            iptables.create_rule()
        else:
            module.exit_json(changed=False, msg="rule already exists.")
    if iptables.state == 'absent':
        if not iptables.check_rule():
            iptables.delete_rule()
        else:
            module.exit_json(changed=False, msg="rule does not exist.")

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()

