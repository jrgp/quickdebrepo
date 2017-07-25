from setuptools import setup, find_packages

setup(name='quickdebrepo',
      version='0.0.1',
      py_modules=['qdr'],
      author='Joe Gillotti',
      author_email='joe@u13.net',
      entry_points={
          'console_scripts': [
              'quickdebrepo = qdr:main',
          ]
      },
)
