user=$1
hostname=$2
restart=${3:-"true"}

[[ -z ${user} ]] && echo "user is unset" && exit 1
[[ -z ${hostname} ]] && echo "hostname is unset" && exit 1

if [[ $restart == "true" ]]; then
    ssh ${user}@${hostname} sudo systemctl restart photobooth-capture
    ssh ${user}@${hostname} systemctl status photobooth-capture
fi
