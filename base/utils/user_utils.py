# -*- coding: utf-8 -*-
import pickle


def get_school(email, domain=None, school_dir=None):
    """
        Fetch the school from email domain
    """
    if domain is None:
        domain = email.split("@")[1].split(".")[::-1]
    if school_dir is None:
        with open("base/static/data/school_directory.pkl", 'rb') as f:
            school_dir = pickle.load(f)
    for n, i in enumerate(domain):
        if i + ".txt" in school_dir.keys():
            return school_dir[i + ".txt"]
        elif i in school_dir.keys():
            return get_school(email, domain[n+1:], school_dir[i])
        else:
            return False
    return school_dir[domain]
