from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='latex_generator_for_tables_and_images',
  version='0.0.2',
  author='Artem',
  author_email='Artems2311@mail.ru',
  description='A library to generate code for tables and images.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://example.com',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  python_requires='>=3.6'
)