if [ "$#" -eq 0 ]; then
	echo "ftpgetfolder <config file>"
	echo "with config file has:"
	echo "	- SERVER=<server address>"
	echo "	- USER=<user name>"
	echo "	- PASSWD=<user password>"
	echo "	- LOCAL_DIR=<path to copy ftp folder/files>"
	echo "	- DISTANT_DIR=<ftp folder to copy from>"
	exit
fi

if [ ! -f $1 ] 
then
	echo ERROR: Config file "$1" does not exist
	exit
fi

source $1

if [ -z "$USER" ] 
then
	ERR=USER is empty
fi 

if [ -z "$PASSWD" ] 
then
	ERR=PASSWD is empty
fi

if [ -z "$SERVER" ] 
then
	ERR=SERVER is empty
fi 

if [ -z "$LOCAL_DIR" ] 
then
	ERR=LOCAL_DIR is empty
fi

if [ -z "$DISTANT_DIR" ] 
then
	ERR=DISTANT_DIR is empty
fi

if [ ! -z "$ERR" ] 
then
	echo ERROR: $ERR
	exit
fi

DATE_SUFFIX=`LC_TIME=C.UTF-8 date '+%d%b%y_%Hh%M.%s'`
LOG=$LOCAL_DIR/getfolder$DATE_SUFFIX.log
PYTHON_FILE=~/Documents/scripts/python/ftpmirror.py

echo Log File: $LOG

python $PYTHON_FILE -s $SERVER -l $LOCAL_DIR -r $DISTANT_DIR -u $USER -p $PASSWD ${@: 2}  > $LOG 

echo >> $LOG
echo ------------------- empty directories:  ------------------- >>  $LOG
cat $LOG | grep WARN >> $LOG

