from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='mnnai',
  version='5.2.0',
  author='mkshustov',
  author_email='reverse.api.mnn@gmail.com',
  description='Module for using MNN API',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/mkshustov/MNNAI',
  packages=find_packages(),
  install_requires=['requests>=2.25.1', 'aiohttp'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='ai MNN chatgpt mnnai mnn',
  project_urls={
    'Documentation': 'https://github.com/mkshustov/MNNAI',
    'Site': 'https://mnnai.ru'
  },
  python_requires='>=3.7'
)
