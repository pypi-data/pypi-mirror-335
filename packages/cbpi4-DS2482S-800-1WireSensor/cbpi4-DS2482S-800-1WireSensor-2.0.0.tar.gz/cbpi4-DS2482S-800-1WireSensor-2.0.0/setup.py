from setuptools import setup

setup(name='cbpi4-DS2482S-800-1WireSensor',
      version='2.0.0',
      description='CraftBeerPi Plugin',
      author='Lawrence Wagy',
      author_email='lnwagy@gmail.com',
      url='https://WagyHof.com',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-DS2482S-800-1WireSensor': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-DS2482S-800-1WireSensor'],
     )
