from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r', encoding="utf-8") as file:
    return file.read()

setup(
  name='loggeringpy',
  version='0.9.1',
  author='K1ayPVA',
  author_email='kegor6137@gmail.com',
  description='Module for sumple logging',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/K1AYPVA/loggeringpy',
  packages=find_packages(),
  install_requires=['colorama>=0.4.6',
                    'dacite>=1.9.2'
                    ],
  classifiers=[
    'License :: OSI Approved :: MIT License'

  ],
  keywords='log logs python ',
  project_urls={
    'Documentation': 'https://github.com/K1AYPVA/loggeringpy/tree/main'
  },
  python_requires='>=3.10'
)