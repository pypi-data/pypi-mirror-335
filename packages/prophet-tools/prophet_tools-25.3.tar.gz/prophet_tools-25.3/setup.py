from setuptools import setup

setup(name='prophet_tools',
      version='25.3',
      description='ProPHet personal tools',
      packages=['prophet_tools'],
      author_email='prophet.incorporated@gmail.com',
      install_requires=[
          'xlsxwriter==3.2.0',
          'pillow==10.1.0',
          'pillow-avif-plugin==1.4.3',
          'comtypes==1.4.7',
          'pymediainfo==6.1.0',
      ],
      zip_safe=False)
