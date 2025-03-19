FROM centos:7
LABEL \
    name="rpkg test for Python 2" \
    description="Run tests using tox with Python 2" \
    vendor="rpkg developers" \
    license="MIT"

RUN yum -y update && yum -y install \
        python2-devel \
        python2-openidc-client \
        python2-setuptools \
        rpmlint \
        rpm-build
# development packages that are not part of packages' specfile \
RUN yum -y install \
        rpm-devel \
        gcc \
        libcurl-devel \
        krb5-devel \
        openssl-devel \
        make \
        git
# Python 3 packages needed for building some python dependencies
# while Python 2 are not available or outdated
RUN yum -y install \
        python3-pip \
        python3-devel
RUN yum clean all

# python-tox in yum repo is too old, let's install latest version
RUN pip3 install tox

WORKDIR /src

COPY . .

CMD ["tox", "-e", "py27,flake8python2"]
