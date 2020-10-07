# Docker commands and DB setup
DB_HOST='localhost'

## efp browser
docker run --restart=always -d --name efp-actinidia -p 58765:80 efp:1.1

## SQL DB server setup
# Start server
docker run --restart=always -d --name efp-actinidia-DB -p 58766:3306 -e MYSQL_ROOT_PASSWORD=efpdbroot -e MYSQL_USER=efpuser -e MYSQL_PASSWORD=efppass mariadb:latest

# Load Databases
BACKUP_DIR=/PATH_TO/eFP_Browser/dbbackups/*.sql.gz
for BACKUP in $BACKUP_DIR
do
    zcat $BACKUP | mysql -u root -pefpdbroot -h $DB_HOST -P 58766
done

# Add privilages for DB user
mysql -u root -pefpdbroot -h $DB_HOST -P 58766 -e "GRANT SELECT ON *.* TO 'efpuser'@'%';"
