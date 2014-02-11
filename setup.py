#!/usr/bin/env python


from setuptools import setup, find_packages

version = '2.1.1-dev'

setup(
    name='gu.plone.rdf',
    version=version,
    description="Plone RDF Integration",
    # long_description=open("README.txt").read() + "\n" +
    #                  open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='',
    author='',
    author_email='',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gu', 'gu.plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
        'plone.app.registry',
        'gu.z3cform.rdf',
        'ordf',
        'rdflib-zodb',
        'collective.z3cform.datetimewidget',
        'collective.monkeypatcher'
    ],
    extras_require={
        'test': ['plone.app.testing', ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
