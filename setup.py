from setuptools import setup, find_packages

setup(name='quickdebrepo',
      version='0.0.2',
      license='MIT',
      description='Quickly host your own debian/apt repo',
      author='Joe Gillotti',
      author_email='joe@u13.net',
      py_modules=['qdr'],
      entry_points={
          'console_scripts': [
              'quickdebrepo = qdr:main',
          ]
      },
)
