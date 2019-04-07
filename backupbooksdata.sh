function error_handler () {
	echo $1 $?
	exit $?
}

FTP_SERVER=ftp.byethost13.com
TMP=~/temp
DATE_SUFFIX=`LC_TIME=C.UTF-8 date '+%d%b%y_%Hh%M.%s'`
LOCAL_DIR=$TMP/BACKUP_$DATE_SUFFIX
DISTANT_DIR=/htdocs/books/img
PYTHON_FILE=~/scripts/python/ftpmirror.py
LOG=$TMP/backup_$DATE_SUFFIX.log

if [ $# -gt 0 ] && [ -f $1 ]; then 
	echo load parameters from $1
	source $1
fi

echo FTP Server: $FTP_SERVER
echo TMP Folder: $TMP
echo LOCAL Dir: $LOCAL_DIR
echo DISTANT Dir: $DISTANT_DIR
echo PYTHON File: $PYTHON_FILE
echo LOG File: $LOG

mkdir $LOCAL_DIR

python $PYTHON_FILE -s $FTP_SERVER -l $LOCAL_DIR -r $DISTANT_DIR -u b13_17778490 -p Motdepasse21! > $LOG || error_handler "Python FTP script error: exit bash"

echo >> $LOG
echo ------------------- empty directories:  ------------------- >>  $LOG
cat $LOG | grep WARN >> $LOG

echo >> $LOG
echo ------------------- file diff:  ------------------- >>  $LOG
ls  $LOCAL_DIR/img/ > $TMP/local.txt 
listftp.sh > $TMP/ftp.txt
cmpbookimg.sh $TMP/ftp.txt $TMP/local.txt >> $LOG
rm -f $TMP/local.txt
rm -f $TMP/ftp.txt

echo >> $LOG
echo ------------------- zip folder:  ------------------- >>  $LOG
ZIPNAME=backupImg.$DATE_SUFFIX.zip
if [ -f $ZIPNAME ]; then
	rm -f $ZIPNAME
fi
zip -r $ZIPNAME $LOCAL_DIR >> $LOG 

rm -fr $LOCAL_DIR

echo ------------------- end script  ------------------- >>  $LOG
