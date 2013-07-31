from setuptools import setup

version = '0.20.2'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-celery',
    'django-kombu',
    'django-extensions',
    'django-nose',
    'lizard-ui >= 4.0b4',
    'lizard-map',
    'pkginfo',
    'xlrd',
    'xhtml2pdf',
    # 'pisa',
    'reportlab',
    'html5lib',
    'pyPdf',
    'factory_boy',
    'lizard-management-command-runner',
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
