FROM bgruening/galaxy-stable
MAINTAINER Tiago Antao <tiagoantao@gmail.com>

RUN apt-get update
RUN apt-get install -y libsasl2-dev libldap2-dev proftpd-mod-ldap
RUN apt-get install -y openssh-server

#COPY startup /usr/bin
#COPY export_user_files.py /usr/local/bin
COPY copy/etc/galaxy.ini /etc/galaxy
COPY copy/etc/reports_wsgi.ini /etc/galaxy
COPY copy/galaxy-central/config/auth_conf.xml /galaxy-central/config
COPY copy/etc/supervisor/conf.d/galaxy.conf /etc/supervisor/conf.d
COPY copy/etc/proftpd/modules.conf /etc/proftpd
COPY copy/etc/proftpd/proftpd.conf /etc/proftpd

#Install Linking of configuration files and entrypoint
RUN wget --no-check-certificate  https://raw.githubusercontent.com/tiagoantao/mutable_files/master/link_mutable_files.py -O /sbin/link_mutable_files.py 
COPY copy/sbin/server_run.sh /sbin
RUN chmod a+x /sbin/server_run.sh /sbin/link_mutable_files.py
RUN mkdir /traverse

COPY copy/etc/ssh/sshd_config /etc/ssh/
RUN ssh-keygen -A
RUN mkdir /var/run/sshd
RUN mkdir /root/.ssh
COPY authorized_keys /root/.ssh

CMD /sbin/server_run.sh