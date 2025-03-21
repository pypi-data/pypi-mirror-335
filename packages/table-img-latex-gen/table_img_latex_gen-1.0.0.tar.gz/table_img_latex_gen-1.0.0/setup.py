from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='table_img_latex_gen',
  version='1.0.0',
  author='Anny-waay',
  author_email='ann.komova@gmail.com',
  description='Module for generation table and image in LaTeX',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='LaTex',
  python_requires='>=3.7',
  license='MIT'
)