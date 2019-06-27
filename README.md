Upvote.pub
---

This site was forked and modified heavily from [codelucas/flask_reddit](https://github.com/codelucas/flask_reddit). The site was originally build for Google App Engine, however, there are likely much cheaper ways to host a site like this.

The site was featured on [Hacker News](https://news.ycombinator.com/item?id=16273171), drawing mixed criticism, but many positive emails and people interested in the code. After failing to gain much steam I shut it down.

If you are interested in using this code, the first thing I would do is remove Google from the equation so you can host anywhere. Feel free to create a pull request if you are successful in doing so!

# Screenshots

![screenshot 1](/images/screen1.png)
<small>Submission Screen</small>

![screenshot 1](/images/screen2.png)
<small>Publication Screen</small>

# `configs.py`

The configs.py file was used to define a lot of the important information about the application like secret keys - and a lot of that information was in turn obtained from google datastore. However, I have commented these sections out to get the site to work locally so people can experiment with it easier.

# Setup and Installation

First - the site is not completely functional with the setup below. If you are interested in using this going forward you will need to make some substantial changes to get things to work. But the below steps will get you something that does run so you can at least see how it works.

1. Clone the repo
2. Build the dockerfile (`Docker build`)
3. Run using the information below:

```
docker build -t upvote .
docker run -it --rm -p 8080:8080 -h 127.0.0.1  -t upvote:latest
```

I use direnv to set configuration variables, and the `.envrc` file looks like this:

```
export FLASK_APP=base/__init__.py
export GAE_VERSION=local-0-1-1-v2
export FLASK_DEBUG=1 # Set to 0 to turn off debugging
gcloud config configurations activate upvote # Used to set the gcloud configuration
export GOOGLE_APPLICATION_CREDENTIALS=gcloud_credentials.json # GCLOUD application credentials
export PYTHONPATH=$(pwd):${PYTHONPATH}
export WERKZEUG_DEBUG_PIN=off
alias run_docker="docker run -d --env-file <(cat .envrc | grep -v '#' | cut -f 2 -d ' ')  -p 8080:8080 -h 127.0.0.1  -t upvote:latest"
export run_docker
```

# Default user

* username - test@upvote.pub
* password - Chicago

# Additions

I added threaded comments and upvoting to comments
