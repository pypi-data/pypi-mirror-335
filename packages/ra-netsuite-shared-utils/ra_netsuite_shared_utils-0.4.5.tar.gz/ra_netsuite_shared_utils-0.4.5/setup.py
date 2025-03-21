from setuptools import setup, find_packages

setup(
    name="ra_netsuite_shared_utils",
    version="0.4.5",
    author="Vrishabh Agamya",
    packages=find_packages(),
    install_requires=[
        "requests",
        "requests-oauthlib",
        "google-cloud-storage",
        "google-cloud-pubsub",
        "google-cloud-tasks",
    ],
)
