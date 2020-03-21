import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# python3 setup.py sdist
# python3 -m twine upload

setup(
    name='django-form-builder',
    version='0.8.5',
    packages=find_packages(),
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
        'filesig>=0.3'
    ],
)
