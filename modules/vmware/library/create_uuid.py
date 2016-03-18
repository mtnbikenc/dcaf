#!/bin/python
# Create a simple UUID

import uuid


def main():
    module = AnsibleModule(
        argument_spec=dict(),
        supports_check_mode=True
    )

    this_uuid = str(uuid.uuid4())

    module.exit_json(uuid=this_uuid)


# import module snippets
from ansible.module_utils.basic import *

main()
