from setuptools import setup, find_packages

setup(
    name='google_drive_connector',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "PyYAML"
    ],
    author="Sai Kiran Kyama",
    author_email="saikiran41101@gmail.com",
    description="A Python package for Google Drive integration",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
