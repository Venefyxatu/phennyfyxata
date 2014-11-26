# Only nanowars for testing purposes for now - will see about making it a full Phennyfyxata box later
FROM ubuntu:14.04
MAINTAINER Erik Heeren <venefyxatu@gmail.com>
# First the big system requirements
RUN apt-get update && apt-get install -y --force-yes apache2 mysql-server-5.6 git libapache2-mod-wsgi pwgen
# Then the Python requirements
RUN apt-get install -y --force-yes python-django django-tables

# Now configure mysql
ADD configure_mysql.sh /configure_mysql.sh
RUN chmod 755 /configure_mysql.sh
RUN /configure_mysql.sh

RUN mkdir -p /opt/projects
RUN git clone https://github.com/sbp/phenny /opt/projects/phenny
RUN git clone https://github.com/Venefyxatu/Phennyfyxata /var/www/html/venefyxatu.be/phennyfyxata
RUN ln -s /var/www/html/venefyxatu.be/phennyfyxata/phenny/nanowars.py -t /opt/projects/phenny/modules
#RUN python /var/www/html/venefyxatu.be/phennyfyxata/manage.py syncdb
