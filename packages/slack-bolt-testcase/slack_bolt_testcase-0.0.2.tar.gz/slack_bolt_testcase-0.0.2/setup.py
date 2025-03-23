import os
from setuptools import setup, find_packages

root_dir_path = os.path.dirname(os.path.abspath(__file__))

long_description = open(os.path.join(root_dir_path, 'README.md')).read()

setup(
    name='slack-bolt-testcase',
    version='0.0.2',
    author='Diego J. Romero López',
    author_email='diegojromerolopez@gmail.com',
    description='Test case for your Slack bots',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=['slack_bolt~=1.23.0', 'slack_sdk~=3.35.0'],
    license='MIT',
    keywords='slack unittest mock',
    url='https://github.com/diegojromerolopez/slack-bolt-testcase',
    packages=find_packages(),
    data_files=[],
    include_package_data=True,
    scripts=[]
)
