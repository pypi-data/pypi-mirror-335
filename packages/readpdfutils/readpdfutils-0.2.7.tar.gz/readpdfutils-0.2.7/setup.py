from distutils.core import setup, Extension
import numpy
import sys
from os import getenv
import sysconfig

arch = sysconfig.get_platform()
arch = arch.replace("android-24-", "")

PLATFORM = sys.platform

if getenv('LIBLINK'):
    PLATFORM = 'android'


library_dirs = ['lib/' + arch]

extension = Extension('readpdfutils', ['utils.c', 'pdf.c'], libraries=["pdfium"], library_dirs=library_dirs, include_dirs=["include", numpy.get_include()])
setup(name="utils",
      version="0.2.7",
      ext_modules = [
        extension
    ]
)
