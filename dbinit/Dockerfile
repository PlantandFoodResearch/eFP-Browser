# Efp DB
FROM mariadb:latest
MAINTAINER ben.warren@plantandfood.co.nz

# Add DB data to load on startup
COPY dbdumps/*.sql.gz /docker-entrypoint-initdb.d/

# Add efp user permissions script
COPY init-efp-user-perms.sql /docker-entrypoint-initdb.d/

# Leave the rest up to mariadb defaults
