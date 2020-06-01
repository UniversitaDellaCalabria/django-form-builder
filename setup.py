import os
from glob import glob
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

#  rm -R build/ dist/ *egg-info
#  python3 setup.py sdist
#  twine upload dist/*

setup(
    name='django-form-builder',
    version='0.9.18-3',
    packages=find_packages(),
    package_data={'': ['*.wav']},
    data_files=[
        ('', glob('django_form_builder/data/audio_captcha/*/default.wav', recursive=True)),
    ],
    include_package_data=True,
    license='BSD License',
    description="Django Form builder",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/UniversitaDellaCalabria/django-form-builder',
    author='Giuseppe De Marco, Francesco Filicetti',
    author_email='giuseppe.demarco@unical.it, francesco.filicetti@unical.it',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'django>=2.0,<4.0',
        'filesig>=0.3',
        'cryptography>=2.8',
        'captcha==0.3'
    ],
)
