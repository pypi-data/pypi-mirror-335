from setuptools import setup, find_packages

setup(
    name='nosql-bulk-automation-package-tst',
    version='0.0.23',
    packages=find_packages(), 
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'nosql-bulk-generate = nosql_bulk_automation_package_tst.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'nosql_bulk_automation_package_tst': [
            'fileGenerator/sizings/*.yaml', 
        ],
    },

)
