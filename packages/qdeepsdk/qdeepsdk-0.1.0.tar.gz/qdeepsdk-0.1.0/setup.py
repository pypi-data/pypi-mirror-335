from setuptools import setup, find_packages

setup(
    name="qdeepsdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['numpy>=1.18.0', 'requests>=2.24.0'],
    author="Suleiman Karim Eddin",
    author_email="suleimankareem90@gmail.com",  # Add your email if appropriate
    description="QDeep QUBO Solver",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # Remove public URL or replace with internal documentation link if available
    # url="https://internal.company.com/docs/qdeep-client",  # Optional internal URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.7',
)