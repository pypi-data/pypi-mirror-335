from setuptools import setup

setup(name='cbpi4_MCP23017Actor',
      version='2.0.0',
      description='CraftBeerPi Plugin',
      author='Lawrence Wagy',
      author_email='lnwagy@gmail.com',
      url='https://WagyHof.com',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_MCP23017Actor': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_MCP23017Actor'],
     )
