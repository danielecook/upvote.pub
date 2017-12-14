# -*- coding: utf-8 -*-
"""
All code for scraping images and videos from posted
links go in this file.
"""
import requests

import click
from base import app

@app.cli.command()
def generate_id_db():
    """Initialize the ID database"""
    click.echo('Init the db')