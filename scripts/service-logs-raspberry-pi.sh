user=$1
hostname=$2

[[ -z ${user} ]] && echo "user is unset" && exit 1
[[ -z ${hostname} ]] && echo "hostname is unset" && exit 1

ssh ${user}@${hostname} journalctl -u photobooth-capture -f
