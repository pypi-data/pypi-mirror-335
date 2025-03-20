from os import path, walk
from setuptools import setup, find_packages
from setuptools.dist import Distribution

NAME = "Orange3-Tools"

VERSION = "0.0.12"

DESCRIPTION = "Tools para Asignatura Big Data Master EERR"
LONG_DESCRIPTION = ""

LICENSE = "GPL-3.0"

KEYWORDS = (
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'orange3 add-on',
)

PACKAGES = find_packages()

print(PACKAGES)

PACKAGE_DATA = {
    'orangecontrib.tools.widgets': ['icons/*'],
}

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = [
    'anyqt',
    'pandas',
    'BeautifulSoup4',
    'numpy',
    'seaborn',
    'Orange3 >=3.31.1',
    'orange-widget-base',
    'scikit-learn',
    'pyqtgraph',
    'mysql-connector-python',
]

EXTRAS_REQUIRE = {
    'doc': ['sphinx', 'recommonmark', 'sphinx_rtd_theme'],
    'test': ['coverage'],
}

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'tools = orangecontrib.tools',
    ),
    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    #'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
    #    'educationaltutorials = orangecontrib.educational.tutorials',
    #),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/example/widgets/__init__.py
        'Tools = orangecontrib.tools.widgets',
    ),

    # Register widget help
    #"orange.canvas.help": (
    #    'html-index = orangecontrib.educational.widgets:WIDGET_HELP_PATH',)
}

NAMESPACE_PACKAGES = ["orangecontrib"]

AUTHOR = 'Julio J. Melero'
AUTHOR_EMAIL = 'melero@unizar.es'
URL = ""
DOWNLOAD_URL = ""

#def include_documentation(local_dir, install_dir):
#    global DATA_FILES

#    doc_files = []
#    for dirpath, _, files in walk(local_dir):
#        doc_files.append((dirpath.replace(local_dir, install_dir),
#                          [path.join(dirpath, f) for f in files]))
#    DATA_FILES.extend(doc_files)

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

if __name__ == '__main__':
    #include_documentation('doc/_build/html', 'help/orange3-educational')
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        #namespace_packages=NAMESPACE_PACKAGES,
        include_package_data=True,
        zip_safe=False,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,
        classifiers = []
#        distclass=BinaryDistribution
    )
