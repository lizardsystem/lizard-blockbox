from setuptools import setup

version = '0.1'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-extensions',
    'django-nose',
    'lizard-ui >= 4.0b4',
    'pkginfo',
    'xlrd',
    ],

tests_require = [
    ]

setup(name='lizard-blockbox',
      version=version,
      description="Lizard Blockbox",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Roland van Laar',
      author_email='roland.vanlaar@nelen-schuurmans.nl',
      url='https://github.com/lizardsystem/lizard-blockbox',
      license='GPL',
      packages=['lizard_blockbox'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
