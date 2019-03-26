BOOK_HELPER_FOLDER=~/scripts/python
PATH=$PATH:$BOOK_HELPER_FOLDER/bookhelper
TYPES=""
export PYTHON=`which python3`

PYTHONPATH=${BOOK_HELPER_FOLDER}
echo PYTHONPATH=$PYTHONPATH

if [ -z $1 ]; then
				echo no arguments provided. exit
				exit
fi

URL_FILE=$1

CMD="$PYTHON  $BOOK_HELPER_FOLDER/bookhelper/main.py $URL_FILE"
shift

while (( "$#" )); do
				if [ -n "$1" ]; then
								TYPES="$TYPES $1"
				fi
				shift
done

CMD="$CMD -f $URL_FILE -t $TYPES"
echo Executing $CMD
$CMD
