from setuptools import setup, find_packages

name = 'nameko-docker'

setup(
    name=name,
    version='0.1.0',
    description='Docker dependency and entrypoints for nameko services.',
    author='Steven Armstrong',
    author_email='steven-%s@armstrong.cc' % name,
    url='http://github.com/asteven/nameko-docker',
    packages=find_packages(),
    install_requires=[
        'nameko',
        'docker',
    ],
    license='GNU General Public License v3 or later (GPLv3+)',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)

