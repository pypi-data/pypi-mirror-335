from setuptools import find_packages, setup

from payment_provider.configuration import __version__

desc = """
    Paymentprovider python sdk. 
    README - https://github.com/hutkorg/python-sdk/blob/master/README.md
  """

requires_list = [
    'requests',
    'six'
]

setup(
    name='payment_provider',
    version=__version__,
    url='https://github.com/hutkorg/python-sdk.git',
    license='MIT',
    description='Python SDK for payment_provider clients.',
    long_description=desc,
    author='Artur Savchenko',
    packages=find_packages(where='.', exclude=('tests*',)),
    install_requires=requires_list,
    classifiers=[
        'Environment :: Web Environment',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ])
