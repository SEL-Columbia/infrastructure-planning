from os.path import abspath, dirname, join
from setuptools import find_packages, setup


FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst', 'CHANGES.rst'])
setup(
    name='infrastructure-planning',
    version='3.0.1',
    description='Infrastructure planning tools',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python'
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='https://github.com/sel-columbia/infrastructure-planning',
    keywords='infrastructure-planning networkplanner crosscompute',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        # 'GDAL',
        'geometryIO>=0.9.7.4',
        'geopy',
        'invisibleroads-macros>=0.7.4',
        'matplotlib',
        # 'networker',
        'networkx<2',
        'numpy',
        'pandas',
        'python-dateutil',
        'scikit-learn',
        'scipy',
        # 'sequencer',
        'shapely',
        'simplejson',
        'six',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ])
