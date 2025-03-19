from setuptools import setup, find_packages
import os

# Function to read the version number from __version__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'wsa_toetsing_tool', '__version__.py')
    with open(version_file) as f:
        exec(f.read())
    return locals()['__version__']

setup(
    name='wsa-toetsing-tool',
    version=read_version(),
    author='Emiel Verstegen',
    author_email='emiel.verstegen@rhdhv.com',
    description='Postprocessing tool voor WSA toetsing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://hhdelfland.visualstudio.com/Waterhuishouding/_git/WSA_toetsing_tool',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'bergingstoets=wsa_toetsing_tool.bergingstoets:main',
            'knelpuntanalyse=wsa_toetsing_tool.knelpuntanalyse:main',
            'samenvoegen_resultaten=wsa_toetsing_tool.samenvoegen_resultaten:main',
            'compensatie_toetshoogte=wsa_toetsing_tool.compensatie_toetshoogte:main',
            'compensatie_scenarios=wsa_toetsing_tool.compensatie_scenarios:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='GPL-3.0',
)