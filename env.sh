export FLASK_APP="/app/base/__init__.py"
export GAE_VERSION=local-0-1-1-v2
export FLASK_DEBUG=1 # Set to 0 to turn off debugging
# no longer used
# config configurations activate upvote # Used to set the gcloud configuration
# GOOGLE_APPLICATION_CREDENTIALS=gcloud_credentials.json # GCLOUD application credentials
export PYTHONPATH=$(pwd):${PYTHONPATH}
export WERKZEUG_DEBUG_PIN=off
export ENV_PORT=8080
source activate env
