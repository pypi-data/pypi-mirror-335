from setuptools import setup

setup(
    name='thatsnakelang',
    version='0.4',
    packages=['hello_world'],
    description='A simple Hello World module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='reggi',
    author_email='thomas.reggi@gmail.com',
    url='https://github.com/reggi/thatsnakelang',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
