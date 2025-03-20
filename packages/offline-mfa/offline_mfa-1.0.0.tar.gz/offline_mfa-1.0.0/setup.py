from setuptools import setup, find_packages

setup(
    name="offline_mfa",  # Package name
    version="1.0.0",  # Package version
    author="Abhishek N Nairy",
    author_email="n.abhishek@isteer.com",
    description="A secure offline MFA system using TOTP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/offline_mfa",  # Update with your repo
    packages=find_packages(include=["app", "app.*"]),  # Finds all Python packages inside 'app/'
    install_requires=[
        "pyotp", 
        "cryptography", 
        "mysql-connector-python",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "offline-mfa=app.main:main",
        ],
    },
)
