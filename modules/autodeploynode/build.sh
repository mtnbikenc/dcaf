#!/usr/bin/env bash

# DCAF AutoDeploy Node Installation
# =================================
# Prior to running this script, the following exports must be configured
# when running on Red Hat Enterprise Linux
# export RHN_USER="username"
# export RHN_PASS="password"    # escape dollar signs (\$)
# export RHN_POOL="pool_id"     # 32-char pool ID

# Optionally you may set ANSIBLE_BUILD to a specific Ansible release tag. This
# option allows for automated build testing against different Ansible versions.
# If the variable is unset the following default will be used.
: ${ANSIBLE_BUILD:=v2.1.0.0-1}

# Once these prerequisites are in place, the script can be executed by:
# curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash

set -e -o pipefail

# Check OS Release to determine if we need to register to RHSM
if [ -f /etc/os-release ]; then
    # Source the file
    . /etc/os-release
    # If we are running on RHEL
    if [ "${NAME}" == "Red Hat Enterprise Linux Server" ]; then
        if [[ $(subscription-manager version) != *"Red Hat Subscription Management"* ]]; then
            # Check for empty/undefined required environment variables
            if [[ -z ${RHN_USER} || -z ${RHN_PASS} || -z ${RHN_POOL} ]]; then
                echo "ERROR: Environment variables RHN_USER, RHN_PASS and RHN_POOL must be defined."
                exit 1
            else
                # Registering system with Red Hat Subscription Management
                subscription-manager register --username=${RHN_USER}  --password=${RHN_PASS}
                subscription-manager attach --pool=${RHN_POOL}
                subscription-manager repos --disable=*
                subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-openstack-6.0-rpms --enable=rhel-server-rhscl-7-rpms --enable=rhel-ha-for-rhel-7-server-rpms
            fi
        fi
    fi
fi

# Installing packages required to build and install Ansible
yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y install git wget rpm-build make asciidoc python2-devel python-setuptools

# Cloning and building Ansible
git clone git://github.com/ansible/ansible.git --recursive
cd ansible/
git checkout ${ANSIBLE_BUILD}
git submodule update --init --recursive
make rpm
yum -y --nogpgcheck localinstall ./rpm-build/ansible-*.noarch.rpm
cd ..

# Cloning DCAF and starting AutoDeployNode build
wget https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/initial_stage.yml
ansible-playbook initial_stage.yml
ansible-playbook /opt/autodeploy/projects/dcaf/modules/autodeploynode/main.yml
