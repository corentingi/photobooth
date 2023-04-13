user=$1
hostname=$2
restart=${3:-"true"}
git_root=$(git rev-parse --show-toplevel)

[[ -z ${user} ]] && echo "user is unset" && exit 1
[[ -z ${hostname} ]] && echo "hostname is unset" && exit 1

echo $git_root

rsync -av --delete \
    --exclude=".git" \
    --exclude="captures" \
    --exclude="processed" \
    --exclude="**/__pycache__" \
    --exclude="photobooth/app/configs/config.yml" \
    ${git_root}/ ${user}@${hostname}:photobooth/

scp ${git_root}/scripts/raspberrypi-config.yml ${user}@${hostname}:photobooth/photobooth/app/configs/config.yml

if [[ $restart == "true" ]]; then
    ssh ${user}@${hostname} sudo systemctl restart photobooth-capture
    ssh ${user}@${hostname} systemctl status photobooth-capture
fi
