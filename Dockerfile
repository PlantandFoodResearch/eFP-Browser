# eFP Browser
FROM centos:centos6

MAINTAINER ben.warren@plantandfood.co.nz

# Yum Packages
RUN yum update -y && yum install -y \
    httpd \
    libjpeg \
    libjpeg-devel \
    zlib \
    zlib-devel \
    freetype \
    freetype-devel \
    mysql \
    python-matplotlib


# httpd config
COPY efp.conf /etc/httpd/conf.d/

# Copy codebase
COPY webcode/ /var/www/html/
RUN chown -R apache:apache /var/www/html

EXPOSE 80

#Running Apache2 server in foreground so it stays open
ENTRYPOINT ["apachectl", "-DFOREGROUND"]
