from setuptools import setup, find_packages

setup(
    name='bpss_file_store_python',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'boto3==1.26.150',
        'azure-storage-blob==12.16.0',
        'google-cloud-storage==2.9.0'
    ],
    # Other metadata and configuration
)
