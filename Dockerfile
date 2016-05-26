FROM ubuntu:14.04

ENV HOME /root

ENV TERM screen-256color

RUN locale-gen --no-purge en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8

RUN apt-get update -qq

ADD conf/apt-packages.txt /tmp/apt-packages.txt
RUN cat /tmp/apt-packages.txt | xargs apt-get --yes --force-yes install
RUN apt-get install freetds-common freetds-bin tdsodbc unixodbc subversion -y
RUN apt-get build-dep pyodbc -y

ADD pip-freeze.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /code

COPY ./ /code/

RUN mkdir -p /var/log/vilogged

ADD conf/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN mkdir -p /etc/supervisor/conf.d && mkdir -p /var/log/supervisor
RUN ln -sf /code/conf/supervisor.vilogged.conf /etc/supervisor/conf.d/vilogged.conf
RUN ln -sf /code/conf/supervisord.conf /etc/supervisor/supervisord.conf

ADD conf/nginx.vilogged.conf /etc/nginx/sites-enabled/default

RUN mkdir -p /var/www/static && chmod -R 760 /var/www/static/ && chown -R www-data:www-data /var/www/static

EXPOSE 5000
EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
CMD ["start"]