__author__ = 'rparra'
from subprocess import call
import os

def jsgf2fsg(file):
    pardir = os.path.dirname(file)
    print pardir
    call(["sphinx_jsgf2fsg", "-jsgf", file, "-fsg", pardir + '/language.fsg'])