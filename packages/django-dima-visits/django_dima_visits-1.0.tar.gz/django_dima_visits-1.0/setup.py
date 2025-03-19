from setuptools import setup, find_packages

setup(
    name='django-dima-visits',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A simple Django app to track page visits for internal use.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='DIMACO',
    author_email='dev@ddmc.ir',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=3.0',
    ],
    python_requires='>=3.6',
)
