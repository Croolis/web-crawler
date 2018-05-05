# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='scheduler',
    version=0.1,
    description='Scheduler for web-crawler',
    author='Vitaly Sopov',
    author_email='kerrovitarr@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'scheduler = scheduler.manage:main',
        ],
    },
)
