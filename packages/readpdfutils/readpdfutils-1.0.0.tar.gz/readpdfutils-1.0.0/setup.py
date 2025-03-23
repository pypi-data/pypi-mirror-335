from distutils.core import setup, Extension
import numpy
import sys
from os import getenv
import sysconfig

arch = sysconfig.get_platform()

print(arch)

arch = arch.replace("android-24-", "")



PLATFORM = sys.platform

if getenv('LIBLINK'):
    PLATFORM = 'android'


library_dirs = ['lib/' + arch]

extension = Extension('readpdfutils', ['readpdfutils.c', 'pdf.c'], libraries=["pdfium"], library_dirs=library_dirs, 
                      include_dirs=["include", numpy.get_include()], extra_link_args=['-Wl,-Bstatic -lpdfium'])
setup(name="readpdfutils",
      version="1.0.0",
      ext_modules = [
        extension
    ]
)
