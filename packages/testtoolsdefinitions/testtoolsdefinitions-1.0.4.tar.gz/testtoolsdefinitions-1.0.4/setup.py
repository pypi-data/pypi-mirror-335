from setuptools import setup, find_packages

setup(
	name="testtoolsdefinitions",
	version="1.0.4",
	description="Singlestore tools definitions",
	author="Jai Khatri",
	author_email="jkhatri@singlestore.com",
	url="https://github.com/singlestore-labs/singlestore-ai-tools",
	packages=find_packages(),
	install_requires=[
		"requests",
		"singlestoredb",
		"python-dotenv"
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
