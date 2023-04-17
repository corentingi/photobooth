directory="/Users/cgitton/Downloads/Impressions Corentin"

mkdir -p "$directory"/printed
mkdir -p "$directory"/converted

find "$directory"/* \
    -maxdepth 0 \
    -type f \
    -print |\
while read line; do
    echo "$line"
    if [[ "$line" == *".HEIC" ]]; then
        magick "$line" "$line".JPG
        mv "$line" "$directory"'/converted/'
        line="$line".JPG
    fi

    lp -d 'Dai_Nippon_Printing_DP_DS620_10x15' -o fit-to-page "$line"
    mv "$line" "$directory"'/printed/'
done;
