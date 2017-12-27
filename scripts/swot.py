#!/usr/bin/env python
# encoding: utf-8
# Author: Daniel E. Cook
#
# This script constructs a swot dataset.
#

import os
import shutil
import pickle
from subprocess import Popen, PIPE
from collections import defaultdict


# Clone the repo
out, err = Popen(['git','clone','https://github.com/leereilly/swot'], stdout=PIPE, stderr=PIPE).communicate()
school_directory = defaultdict()
for root, dirs, files in os.walk("swot/lib/domains"):
    domain_root = root.split("/")[3:]
    current_dir = school_directory
    for i in domain_root:
        if i not in current_dir.keys():
            current_dir[i] = defaultdict()
        current_dir = current_dir[i]
    for file in files:
        domain = file
        if file != ".DS_Store":
            with open(root + "/" + file, 'r',  encoding="utf-8") as f:
                school = f.read().strip().encode('utf-8')
            current_dir[domain] = school.decode('utf-8').split(" In ")[0].strip()

shutil.rmtree("swot")


with open('../base/static/data/school_directory.pkl', 'wb') as f:
    f.write(pickle.dumps(school_directory))

