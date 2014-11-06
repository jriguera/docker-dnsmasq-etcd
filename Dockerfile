# dnsmasq-etcd
#
# VERSION  0.1.0
#
# Use phusion/baseimage as base image.
# https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
#
FROM phusion/baseimage:0.9.15
MAINTAINER Jose Riguera <jriguera@gmail.com>

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

# Delete ssh_gen_keys
RUN rm -rf /etc/service/sshd /etc/my_init.d/00_regen_ssh_host_keys.sh

# Update
RUN apt-get update

# Dnsmasq
RUN apt-get install -y dnsmasq 
 
# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-pip 

# Dependencies for python-etcd
RUN apt-get install -y python-openssl libffi-dev libssl-dev

# Clean
RUN apt-get clean

# Get pip to download and install requirements:
RUN pip install python-etcd

# Install pipework 
ADD https://raw.githubusercontent.com/jpetazzo/pipework/master/pipework /usr/bin/
RUN chmod 0755 /usr/bin/pipework
ENV PIPEWORK_BIN /usr/bin/pipework

# Install confd
ADD https://github.com/kelseyhightower/confd/releases/download/v0.7.0-beta1/confd-0.7.0-linux-amd64 /usr/bin/confd
RUN chmod 0755 /usr/bin/confd
ENV CONFD_BIN /usr/bin/confd

# prepare to run
ADD confd/ /etc/confd/
ADD etcd_leases.py /usr/bin/
RUN chmod 0755 /usr/bin/etcd_leases.py
ADD init/ /etc/my_init.d/
EXPOSE 53

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

