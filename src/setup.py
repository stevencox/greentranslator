from distutils.core import setup 
setup(
      name = 'greentranslator',
      packages = [ 'greentranslator' ], # this must be the same as the name above
      package_dir={ 'greentranslator' : 'greentranslator' },
      package_data={ 'greentranslator' : [
         'query/*.sparql',
         'swagger_client/*',
         'swagger_client/models/*',
         'swagger_client/apis/*'
      ]},
      version = '0.33',
      description = 'Green Team BioMedical Data Translator',
      author = 'Steve Cox',
      author_email = 'scox@renci.org',
      install_requires = [
         'certifi >= 14.05.14',
         'six == 1.10.0',
         'python_dateutil >= 2.5.3',
         'setuptools >= 21.0.0',
         'urllib3 >= 1.15.1',
         'bokeh==0.12.5',
         'numpy==1.12.1',
         'pandas==0.19.2',
         'prov==1.5.0',
         'pydotplus==2.0.2',
         'seaborn==0.7.1',
         'SPARQLWrapper==1.8.0'
      ],
      include_package_data=True,
      url = 'https://github.com/stevencox/greentranslator.git',
      download_url = 'https://github.com/stevencox/greentranslator/archive/0.33.tar.gz',
      keywords = [ 'biomedical', 'environmental', 'exposure', 'clinical' ],
      classifiers = [ ],
    )
