from setuptools import setup, find_packages, Command
import os

VERSION = '0.1.0'
DESCRIPTION = 'deeporigin_molstar'
LONG_DESCRIPTION = 'Biosim Molstar'

os.system('source run_molstar.sh')

setup(name="deeporigin_molstar",
      version=VERSION,
      author="G. Zohrabyan, Kh. Smbatyan",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
            "rdkit",
            "IPython",
      ],
)