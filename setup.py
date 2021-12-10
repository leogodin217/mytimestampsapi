from setuptools import setup, find_packages

setup(
    name='mytimestampsapi',
    version='0.1',
    url='https://github.com/leogodin217/mytimestamps-api',
    author='Leo Godin',
    author_email='leogodin217@gmail.com',
    description='API for managing user timestamps',
    packages=find_packages(),
    install_requires=['alembic', 'fastapi',
                      'sqlalchemy', 'fastapi-utils', 'psycopg']
)
