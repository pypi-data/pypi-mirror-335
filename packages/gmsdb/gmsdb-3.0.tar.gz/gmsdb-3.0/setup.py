from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='gmsdb',
  version='3.0',
  author='Oleg I.Berngardt',
  author_email='berng@rambler.ru',
  description='GMSDB Clusterer',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/berng/GMSDB',
  packages=find_packages(),
  install_requires=['numpy','matplotlib','scikit-learn','mlxtend','scipy','statsmodels'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='clusterization',
  project_urls={},
  python_requires='>=3.6'
)

