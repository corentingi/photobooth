user=$1
hostname=$2
location=${3:-"$HOME/photobooth_photos/"}

[[ -z ${user} ]] && echo "user is unset" && exit 1
[[ -z ${hostname} ]] && echo "hostname is unset" && exit 1

rsync -av ${user}@${hostname}:photos/ $location
