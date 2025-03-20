from setuptools import setup, find_packages

setup(
	name='markerpath',
	version='0.1.17',
	author='gg61021277',
	author_email='gg61021277@gmail.com',
	description='All imports are relative to the presence of the marker file',
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	url='https://github.com/',
	packages=['markerpath'],
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6',
)
