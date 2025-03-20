from setuptools import setup, find_packages

version = '6.1.3'

setup(
    name='django-yarnpkg',
    version=version,
    description="Integrate django with yarnpkg",
    long_description=open('README.rst').read(),
    classifiers=[
        'Framework :: Django',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    author='Dominik George',
    author_email='nik@naturalnet.de',
    url='https://edugit.org/AlekSIS/libs/django-yarnpkg',
    license='Apache-2.0',
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'django',
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
