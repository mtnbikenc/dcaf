#!/usr/bin/env bash
# This script is a copy of the master minimize-rhel-iso.sh found in the Hanlon
# project at https://github.com/csc/Hanlon/blob/master/scripts/minimize-rhel-iso.sh

usage()
{
cat << EOF

Usage: $0 OPTIONS

This script builds a new (minimized) RHEL ISO.

OPTIONS:
   -h, --help                 print usage for this command
   -i, --input-file=FILE      file containing ISO to minimize
   -o, --output-file=FILE     name of ISO file to create

EOF
}

# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -o h,i:o: -l help,input-file:output-file: -- "$@")
then
    usage
    # something went wrong, getopt will put out an error message for us
    exit 1
fi
set -- $options

# loop through the command line arguments, parsing them as we go along
# (and shifting them off of the list of command line arguments as they,
# and their arguments if they have any, are parsed).  Note the use of
# the 'tr' and 'sed' commands when parsing the command arguments. The
# 'tr' command is used to remove the leading and trailing quotes from
# the arguments while the 'sed' command is used to remove the leading
# equals sign from the argument (if it exists).
BUNDLE_TYPE_SELECTED=0
while [[ $# -gt 0 ]]; do
  case $1 in
  -i|--input-file) INPUT_FILE=`echo $2 | tr -d "'" | sed 's:^[=]\?\(.*\)$:\1:'`; shift;;
  -o|--output-file)
      FNAME=`echo $2 | tr -d "'" | sed 's:^[=]\?\(.*\)$:\1:'`;
      cd "$(dirname "$FNAME")";
      OUTPUT_FILE="$(pwd)/$(basename "$FNAME")";
      cd "$OLDPWD";
      shift;;
  -h|--help) usage; exit 0;;
  (--) shift; break;;
  (-*) echo "$0: error - unrecognized option $1" 1>&2; usage; exit 1;;
  esac
  shift
done

# if there are still arguments left, the syntax of the command is wrong
# (there were extra arguments given that don't belong)
if [[ ! $# -eq 0 ]]; then
  echo "$0: error - extra fields included in commmand; remaining args=$@" 1>&2; usage; exit 1
fi

# sanity check the arguments that were parsed to ensure that the required
# arguments are present and the optional ones make sense (in terms of which
# optional arguments were given, and in what combination)
if [[ -z $INPUT_FILE ]] || [[ -z $OUTPUT_FILE ]]; then
  printf "\nError (Missing Argument); the 'input-file' and 'output-file' must both be specified\n"
  usage
  exit 1
fi

# setup a few constants that we'll use elsewhere
BUILD_DIR='/tmp/rhel-image'
ISO_MOUNT='/mnt/cdrom'

# cleanup from previous build if it was interrupted
if [[ ! -d ${BUILD_DIR} ]]; then
    rm -rf ${BUILD_DIR}
fi

if [[ -e /etc/yum.repos.d/rhel-dvd.repo ]]; then
    rm -f /etc/yum.repos.d/rhel-dvd.repo
fi

if [[ -d /var/cache/yum/x86_64/6Server/dvd ]]; then
    rm -rf /var/cache/yum/x86_64/6Server/dvd
fi

# and setup directories needed for this build
mkdir -p ${BUILD_DIR}/Packages
if [[ ! -d ${ISO_MOUNT} ]]; then
    mkdir ${ISO_MOUNT}
fi

# mount the input file
mount ${INPUT_FILE} ${ISO_MOUNT} -o loop

# create a repo in the yum.repos.d directory for the
# DVD image that we just mounted
cat > /etc/yum.repos.d/rhel-dvd.repo <<EOF
[dvd]
name=Red Hat Enterprise Linux Installation DVD
baseurl=file://${ISO_MOUNT}
enabled=0
EOF

# copy over all of the contents from the image **except** for the packages
rsync -av --progress ${ISO_MOUNT}/ ${BUILD_DIR} --exclude Packages

# and then copy over the packages we need from the core, base and
# anaconda-tools package groups
for url in `repoquery --enablerepo=dvd --nevr --qf=%{pkg} -g --list --grouppkgs=all \
  anaconda-tools core base ruby-runtime | xargs repotrack --repoid=dvd -a x86_64 -u`; do
    file=`echo ${url#*/} | cut -d'/' -f2-`
    cp -pv ${file} ${BUILD_DIR}/Packages
done

# get the volume id to use from the isolinux.cfg file in the ISO we're copying from
# (converting any '\x20' character sequences to spaces)
VOL_ID=`grep LABEL ${ISO_MOUNT}/isolinux/isolinux.cfg | \
  sed 's/.*LABEL=\([^ ]\+\) .*/\1/' | head -1` | sed 's/\\x20/ /g'
[ -z ${VOL_ID} ] && VOL_ID='Disk'

echo "creating new iso '${OUTPUT_FILE}' with volume id '${VOL_ID}'..."

cd ${BUILD_DIR}
mkisofs -o ${OUTPUT_FILE} -b isolinux/isolinux.bin -c isolinux/boot.cat \
  --no-emul-boot --boot-load-size 4 --boot-info-table -J -R -V "${VOL_ID}" .

rm -f /etc/yum.repos.d/rhel-dvd.repo
rm -rf /var/cache/yum/x86_64/6Server/dvd
rm -rf ${BUILD_DIR}
umount ${ISO_MOUNT}
