directory="/Users/cgitton/Desktop/Photos à imprimer"
printer_name="Dai_Nippon_Printing_DP_DS620_10x15_NO_CUT"

mkdir -p "$directory"/printed
mkdir -p "$directory"/converted

find "$directory"/* \
    \( -iname "*.jpg" -o  -iname "*.heic" \) \
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

    lp -d "$printer_name" -o fit-to-page "$line"
    mv "$line" "$directory"'/printed/'
done;
