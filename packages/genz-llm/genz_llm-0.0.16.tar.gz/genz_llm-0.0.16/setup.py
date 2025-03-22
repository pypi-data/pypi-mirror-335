from setuptools import setup, find_packages

setup(
    # name="your_project_name",
    # version="0.1.0",
    # author="Your Name",
    # author_email="your_email@example.com",
    # description="A short description of your project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/your_username/your_project",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Add your dependencies here, e.g.,
        # "numpy>=1.18.0",
    ],
    include_package_data=True,
    license="MIT",
)