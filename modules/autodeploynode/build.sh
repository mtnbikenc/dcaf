#!/usr/bin/env bash

# DCAF AutoDeploy Node Installation
# =================================
# Prior to running this script, the following exports must be configured
# when running on Red Hat Enterprise Linux
# export RHN_USER="username"
# export RHN_PASS="password"    # escape dollar signs (\$)
# export RHN_POOL="pool_id"     # 32-char pool ID

# Once these prerequisites are in place, the script can be executed by:
# curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash

set -e -o pipefail

# Check for /etc/os-release
if [ -f /etc/os-release ]; then
    # Source the file
    . /etc/os-release
    # If we are running on RHEL
    if [ "$NAME" == "Red Hat Enterprise Linux Server" ]; then
        # Check for empty/undefined ENV variables
        if [[ -z $RHN_USER || -z $RHN_PASS || -z $RHN_POOL ]]; then
            echo "ERROR: Environment variables RHN_USER, RHN_PASS and RHN_POOL must be defined."
            exit 1
        else
            subscription-manager register --username=$RHN_USER  --password=$RHN_PASS
            subscription-manager attach --pool=$RHN_POOL
            subscription-manager repos --disable=*
            subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-openstack-6.0-rpms --enable=rhel-server-rhscl-7-rpms --enable=rhel-ha-for-rhel-7-server-rpms
        fi
    fi
fi

yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y install git wget rpm-build make asciidoc python2-devel python-setuptools

git clone git://github.com/ansible/ansible.git --recursive
cd ansible/
git checkout v2.0.1.0-1
git submodule update --init --recursive
make rpm
yum -y --nogpgcheck localinstall ./rpm-build/ansible-*.noarch.rpm
cd ..

wget https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/initial_stage.yml
ansible-playbook initial_stage.yml

ansible-playbook /opt/autodeploy/projects/dcaf/modules/autodeploynode/main.yml
