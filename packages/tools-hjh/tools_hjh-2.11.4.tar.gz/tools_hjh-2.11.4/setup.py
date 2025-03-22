from setuptools import setup

setup (
    name='tools_hjh',
    version='2.11.4',
    author='HuaJunhao',
    author_email='huajunhao6@yeah.net',
    install_requires=[
          'dbutils'
        , 'pymysql'
        , 'psycopg2'
        , 'cx_Oracle'
        , 'pandas'
        , 'requests'
        , 'eventlet'
    ],
    packages=['tools_hjh', 'other']
)
