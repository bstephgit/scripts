
if [ "$#" -eq 1 ] && [ "$1" == "stop" ]
then
	echo stopping containers
	docker stop myadmin
	docker stop mysqlserver
	docker stop my-apache-php-app
	exit
fi

MYSQL_ENV="-e MYSQL_DATABASE=bookstoredb -e MYSQL_ROOT_PASSWORD=aldu"

docker run -d -it $MYSQL_ENV  --name=mysqlserver  --rm --mount type=bind,src=/Users/albertdupre/Public/mysqldata,dst=/docker-entrypoint-initdb.d mysql:latest

#docker run --name=mysqlclient -d -e MYSQL_ROOT_PASSWORD=aldu --rm --link=mysqlserver mysql:latest
docker run --name myadmin -d --link=mysqlserver -e PMA_HOST="mysqlserver" -e PMA_PORT=3306 -p 8080:80 --rm phpmyadmin/phpmyadmin

docker run -d -p 80:80 --name my-apache-php-app --link=mysqlserver -v "/Users/albertdupre/Public/php-site":/var/www/html --rm php:7.0-apache

docker exec my-apache-php-app docker-php-ext-install mysqli
docker exec my-apache-php-app docker-php-ext-install apachectl restart

