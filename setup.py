from setuptools import setup

version = "1.7.dev0"

long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]
)

install_requires = (["Django >= 2.2, < 3", "lizard-ui >= 4.50, < 5", "xlrd",],)

tests_require = [
    "django-nose",
    "mock",
    "factory-boy",
]

setup(
    name="lizard-blockbox",
    version=version,
    description="Lizard Blockbox",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python", "Framework :: Django",],
    keywords=[],
    author="Roland van Laar",
    author_email="roland.vanlaar@nelen-schuurmans.nl",
    url="https://github.com/lizardsystem/lizard-blockbox",
    license="GPL",
    packages=["lizard_blockbox", "lizard_map"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={"console_scripts": []},
)
