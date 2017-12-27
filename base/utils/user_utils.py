# -*- coding: utf-8 -*-
import pickle


def get_school(email):
    """
        Fetch the school from email domain
    """
    domain = email.split("@")[1].split(".")[::-1]
    with open("base/static/data/school_directory.pkl", 'rb') as f:
        school_dir = pickle.load(f)
    for i in domain:
        if i + ".txt" in school_dir.keys():
            return school_dir[i + ".txt"]
        try:
            school_dir = school_dir[i]
        except KeyError:
            return False
    return school_dir[domain]

