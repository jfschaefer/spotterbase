from setuptools import setup

setup(
    name='spotterbase',
    version='0.0.1',
    packages=['spotterbase', 'spotterbase.model_core', 'spotterbase.corpora', 'spotterbase.data',
              'spotterbase.dnm', 'spotterbase.dnm_nlp', 'spotterbase.rdf', 'spotterbase.sparql', 'spotterbase.spotters',
              'spotterbase.test', 'spotterbase.utils', 'spotterbase.preprocessing'],
    url='https://github.com/jfschaefer/spotterbase',
    author='Jan Frederik Schaefer',
    author_email='',
    description='Framework for spotters on HTML5 documents',
    license='MIT',
)
