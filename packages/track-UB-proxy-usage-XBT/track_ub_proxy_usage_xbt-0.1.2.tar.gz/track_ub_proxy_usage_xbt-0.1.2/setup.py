from setuptools import setup, find_packages

setup(
    name="track_UB_proxy_usage_XBT",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
    description="A package to monitor third-party proxy usage",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Bhumika Bhatti",
    author_email="bhumika.bhatti@xbyte.io",
    # url="https://github.com/yourusername/track_proxy_usage_XBT",  # Update with your repo
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
