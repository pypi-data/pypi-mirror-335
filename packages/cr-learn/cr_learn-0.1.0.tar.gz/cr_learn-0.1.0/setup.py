from setuptools import setup, find_packages

setup(
    name='cr_learn',
    version='0.1.0',
    author='Vishesh Yadav',
    author_email='sciencely98@gmail.com',
    description='A Library Provides Bundch of datasets to speed up your recsys learing.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vishesh9131/corerec',
    packages=find_packages(),
    classifiers=[
           'Programming Language :: Python :: 3',
           'License :: OSI Approved :: MIT License',
           'Operating System :: OS Independent',
       ],
    python_requires='>=3.6',
   )