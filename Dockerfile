FROM gcr.io/google-appengine/python

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
ca-certificates \
curl \
git \
supervisor \
imagemagick \
ghostscript

# Create a virtualenv for dependencies. This isolates these packages from
# system-level packages.
# Python 3
RUN virtualenv /env -p python3.6

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

# Default Version
ENV IS_DOCKER YES

CMD /usr/bin/supervisord -c /app/supervisord.conf && tail -f /dev/null
