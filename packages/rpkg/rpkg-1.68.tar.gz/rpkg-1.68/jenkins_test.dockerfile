FROM fedora:41
LABEL \
    name="rpkg test" \
    description="Run tests using tox with Python 3" \
    vendor="rpkg developers" \
    license="MIT"

RUN dnf -y update && dnf -y install \
        python3-devel \
        python3-openidc-client \
        python3-libmodulemd \
        python3-rpmautospec \
        python3-setuptools \
        rpmlint \
        rpm-build \
        rpmdevtools
# development packages that are not part of packages' specfile \
RUN dnf -y install \
        python3-tox \
        python3-pip \
        python3.6 \
        rpm-devel \
        gcc \
        libcurl-devel \
        krb5-devel \
        openssl-devel \
        make \
        git \
        bandit
RUN dnf clean all

WORKDIR /src

COPY . .

CMD ["tox", "-e", "py36,py39,py312,py313,flake8,bandit"]
