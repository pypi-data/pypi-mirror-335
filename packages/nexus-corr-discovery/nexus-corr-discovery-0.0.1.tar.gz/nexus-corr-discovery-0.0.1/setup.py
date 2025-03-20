from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name="nexus-corr-discovery", 
        version="0.0.1",
        packages=find_packages(include=["nexus", "nexus.*"]),
    )