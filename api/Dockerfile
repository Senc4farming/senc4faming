FROM hakonamdal/python-gdal:python3.9-gdal3.1.2

RUN  apt-get update  -y --allow-releaseinfo-change \
  && apt-get install -y python3-numpy 
RUN pip install gdal==3.1.2
# install pip
#RUN apt-get update && apt-get -y install python3-pip --fix-missing



# copy source files
COPY conf /app/conf
COPY py /app/py
COPY conf/loginscript.sh /etc/profile
COPY requirements.txt /app/requirements.txt
WORKDIR /app


RUN pip3 install --upgrade pip


#Install wget
RUN  apt-get update  -y --allow-releaseinfo-change \
  && apt-get install -y wget \
  && apt-get install -y curl \
  && apt-get install -y gnupg \ 
  && apt-get install -y gnupg1 \ 
  && apt-get install -y gnupg2 \
  && apt-get install -y apt-utils \
  && apt-get install -y unzip \
  && apt-get install -y \
        apt-utils \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcb-dri3-0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        xdg-utils \
        libpq-dev \
        gcc \
        libgdk-pixbuf2.0-0 \
&& rm -rf /var/lib/apt/lists/*



# install psycopg2 library with PIP
RUN pip3 install psycopg2


# uwsgi must be compiled - install necessary build tools, compile uwsgi
# and then remove the build tools to minimize image size
# (buildDeps are removed, deps are kept)
RUN set -ex \
    && buildDeps=' \
        build-essential \
    ' \
    && deps=' \
        htop \
    ' \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends  && rm -rf /var/lib/apt/lists/* \
    && pip install uWSGI==2.0.19.1 \
    && apt-get purge -y --auto-remove $buildDeps \
    && find /usr/local -depth \
    \( \
        \( -type d -a -name test -o -name tests \) \
        -o \
        \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    \) -exec rm -rf '{}' +

RUN echo 'we are running some # of cool things'

RUN pip --use-deprecated=legacy-resolver install -r /app/requirements.txt

RUN python /app/py/check_sys.py

# background spooler dir
RUN mkdir /tmp/pysrv_spooler
RUN ls /tmp

# we don't need this file with Docker but uwsgi looks for it
RUN echo `date +%s` >/app/VERSION

EXPOSE 80
RUN echo 'we are running some # of cool things'

# our server config file
# - you should write your own config file and put OUTSIDE the repository
#   since the config file contains secrets
# - here I use the sample template from repo
# - it is also possible to override the config with env variables, either here
#   or in Amazon ECS or Kubernetes configuration
COPY conf/server-config.json /app/real-server-config.json
ENV PYSRV_DATABASE_HOST host.docker.internal
# ENV PYSRV_REDIS_HOST host.docker.internal
# ENV PYSRV_DATABASE_PASSWORD x

# build either a production or dev image
ARG BUILDMODE=production
ENV ENVBUILDMODE=$BUILDMODE

RUN echo "BUILDMODE $ENVBUILDMODE"

# run in shell mode with ENV expansion
CMD uwsgi --ini /app/conf/uwsgi.ini:uwsgi-$ENVBUILDMODE