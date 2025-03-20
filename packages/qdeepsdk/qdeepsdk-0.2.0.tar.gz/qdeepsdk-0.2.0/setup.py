from setuptools import setup, find_packages

setup(
    name="qdeepsdk",
    version="0.2.0",
    packages=find_packages(),
    install_requires=['numpy>=1.18.0', 'requests>=2.24.0'],
    author="Ahmad Sarhan",
    author_email="ahmadhasansarhana@gmail.com",
    description="Our hybrid solver for QUBO problems merges classical and quantum computing, efficiently solving complex optimization tasks. It offers fast, accurate results for applications in logistics, finance, and more.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.7',
)