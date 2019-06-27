Upvote.pub
---

Upvote.pub (https://www.upvote.pub) was a shortlived experiment to create a reddit-style clone specifically for scientific publications. Users could submit scientific publications from arXiv, bioRxiv, PubMed, or using a DOI. These submissions could then be upvoted or discussed using a commenting function (which also featured upvotes). I created the site because I like HackerNews and reddit, and I believe more dialogue regarding scientific publications would be a great thing.

The site was [featured on HackerNews](https://news.ycombinator.com/item?id=16273171) and drew mixed criticims. There are some subreddits which provide similar functionality. I have open-sourced this project.

If you are interested in restarting this project or forking / modifying please let me know!

# Screenshots

![screenshot 1](/images/screen1.png)
<small>Submission Screen</small>

![screenshot 1](/images/screen2.png)
<small>Publication Screen</small>

![screenshot 1](/images/screen3.png)
<small>Subs selection screen</small>


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
