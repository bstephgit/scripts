

check_pass_eq(){

	username=$1
	password=$2

	LINE="$(grep $username /etc/shadow | cut -d: -f2)"
	SALT="$(echo $LINE | cut -d$ -f3)"
	HASH="$(echo $LINE | cut -d$ -f4)"

	#echo salt: $SALT hash: $HASH

	PERL="print crypt(\"$password\", \"\\\$6\\\$$SALT\\\$\")"

	#echo $PERL

	perl -e -c "${PERL}" || return 1

	LINE=$username:$(perl -e "${PERL}")
	echo check password: search for $LINE...
	grep $LINE  /etc/shadow > /dev/null || return 1

	return 0
}

if [ $# -lt 2 ]; then
	echo please provide user name and password as arguments
	exit 1
fi

check_pass_eq $1 $2
echo check_pass_eq returned $?

