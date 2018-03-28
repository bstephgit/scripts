REF_FILE=$1
CMP_FILE=$2

cat $REF_FILE | while read LINE ; do

	FOUND=`grep -F -x "$LINE" "$CMP_FILE"`
	if [ -z "$FOUND" ]; then
		echo $LINE
	fi
done
