from distutils.core import setup, Extension
from distutils import util
import numpy 
import sys
import os
from os import getenv

PLATFORM = sys.platform

if getenv('LIBLINK'):
    PLATFORM = 'android'

library_dirs = ['lib/mac-arm64']

extension = Extension('readpdfutils', ['utils.c', 'pdf.c'], libraries=["pdfium"], library_dirs=library_dirs, include_dirs=["include", numpy.get_include()])
setup(name="utils",
      version="0.1.2",
      ext_modules = [
        extension
    ]
)
