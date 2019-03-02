# param: us, fr, etc...
if [ $# -ne 1 ]; then
		echo "provide language argument (us, fr, en-us etc...)"
fi
setxkbmap $1 
