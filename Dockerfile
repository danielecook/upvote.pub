FROM mysql:5.7

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
ca-certificates \
curl \
git \
supervisor \
imagemagick \
ghostscript \
redis-server

RUN apt-get install -y make build-essential libssl-dev zlib1g-dev \
                       libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
                        libncurses5-dev libncursesw5-dev xz-utils tk-dev wget

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz \
&& tar xvf Python-3.6.3.tgz \
&& cd Python-3.6.3 \
&& ./configure --enable-optimizations \
&& make -j8 \
&& make install

RUN apt-get -y install python-pip
RUN pip install virtualenv

# Create a virtualenv for dependencies. This isolates these packages from
# system-level packages.
# Python 3
RUN virtualenv /env -p python3.6

RUN apt-get install -y libmysqlclient-dev

# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add the application source code.
ADD . /app
WORKDIR "/app"

ENV FLASK_APP="/app/base/__init__.py"

RUN apt-get install redis-server

CMD service redis-server start && /etc/init.d/mysql start && mysql -e "CREATE DATABASE docker_db;" && /bin/bash -c "source /env/bin/activate; source env.sh; flask initdb local" && /usr/bin/supervisord -c /app/supervisord.conf && tail -f /dev/null
