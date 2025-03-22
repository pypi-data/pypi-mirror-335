from setuptools import setup, find_packages

setup(
       name='Maxl',
       version='0.1',
       packages=find_packages(),
       description='Library for finding the max in a list.',
       long_description=open('README.md').read(),
       long_description_content_type='text/markdown',
       author='Yaroslava',
       author_email='yarash0607@gmail.com',
       url='https://github.com/Yaraaa2650/Maxl', 
       classifiers=[
           'Programming Language :: Python :: 3',
           'License :: OSI Approved :: MIT License',
           'Operating System :: OS Independent',
       ],
       python_requires='>=3.6',
   )
   
