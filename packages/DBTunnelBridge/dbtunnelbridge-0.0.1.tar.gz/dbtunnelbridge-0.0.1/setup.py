from setuptools import setup, find_packages


# Utility function to read the requirements.txt file
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]


setup(
    name='dbtunnelbridge',
    version='0.0.1',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    description='A package for managing local and remote database connections with optional SSH tunneling.',
    author='Kyle Wilson',
    author_email='',
    url='https://github.com/kwilsonmg/DBTunnelBridge',
)
