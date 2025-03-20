from setuptools import setup, find_packages

setup(
    name="digital-marketing-portfolio",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==3.0.2",
        "python-dotenv==1.0.1",
    ],
    author="Titus Kores",
    author_email="ntimama2@gmail.com",
    description="A modern portfolio website for digital marketing and SEO experts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thadigitalguru/static-website",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "digital-portfolio=src.app:main",
        ],
    },
) 