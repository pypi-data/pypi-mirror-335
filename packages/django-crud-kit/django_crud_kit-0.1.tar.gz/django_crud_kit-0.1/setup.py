from setuptools import setup, find_packages

setup(
    name="django-crud-kit",  # Package name for PyPI
    version="0.1",
    packages=find_packages(),
    include_package_data=True,  # Ensures templates & static files are included
    install_requires=[
        "django>=4.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author="Koded",
    author_email="your-email@example.com",
    description="A reusable CRUD system for Django projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Koded0214h/DjangoCrudKit",  # Your GitHub repo
    python_requires=">=3.6",
)
