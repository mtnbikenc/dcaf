#!/usr/bin/env bash

# DCAF AutoDeploy Node Installation
# =================================
# Prior to running this script, the following exports must be configured
# export RHN_USER="username"
# export RHN_PASS="password"    # escape dollar signs (\$)
# export RHN_POOL="pool_id"     # 32-char pool ID

# Additionally, a pem file should be created to provide access to private GitHub repos
# cat << EOF > ~/github.pem
# -----BEGIN RSA PRIVATE KEY-----
# <insert_key_file_text_here>
# -----END RSA PRIVATE KEY-----
# EOF
# chmod 0600 ~/github.pem

# Once these prerequisites are in place, the script can be executed by:
# curl https://raw.githubusercontent.com/csc/dcaf/master/modules/autodeploynode/build.sh | bash

# TODO Add error handling to exit if a command fails along the way
set -eu -o pipefail

subscription-manager register --username=$RHN_USER  --password=$RHN_PASS
subscription-manager attach --pool=$RHN_POOL
subscription-manager repos --disable=*
subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-openstack-6.0-rpms --enable=rhel-server-rhscl-7-rpms --enable=rhel-ha-for-rhel-7-server-rpms

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
ansible-playbook initial_stage.yml --extra-vars "github_key_file=~/github.pem"
cd /opt/autodeploy/projects/dcaf/modules/autodeploynode

ansible-playbook stage_resources.yml --extra-vars "github_key_file=~/github.pem rhn_user=$RHN_USER rhn_pass=$RHN_PASS"
ansible-playbook main.yml --extra-vars "github_key_file=~/github.pem"
