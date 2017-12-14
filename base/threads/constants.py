# -*- coding: utf-8 -*-

# For simplicity, these values are shared among both threads and comments.
MAX_TITLE = 300
MAX_BODY = 3000
MAX_LINK = 250

MAX_PUB_TITLE = 300
MAX_AUTHORS = 300
MAX_DOI = 100
MAX_JOURNAL = 100

MAX_COMMENTS = 500
MAX_DEPTH = 10

# thread & comment status
DEAD = 0
ALIVE = 1

STATUS = {
    DEAD: 'dead',
    ALIVE: 'alive',
}

