import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

long_description= \
    """The graphical user interface on top of the
       ASE GUI <https://wiki.fysik.dtu.dk/ase/ase>
    """

package = 'tkasegui'
version = __import__(package).__version__

#package_data = {'mstm_studio' : ['images/*.png', 'nk/eta*.txt']}

setuptools.setup(
    name=package,
    version=version,
    author='Leon Avakyan',
    author_email='laavakyan@sfedu.ru',
    description='Unofficial ASE gui extension',
    long_description=long_description,
    #long_description_content_type="text/markdown",
    url='https://gitlab.com/Avakyan/tkasegui',
    packages=setuptools.find_packages(),
    install_requires=[
          'ase'
      ],
    #extras_require={
    #    'GUI': ['matplotlib', 'tkinter', 'pillow'],
    #    'spheroid': ['scatterpy']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    license='GPLv3',
    python_requires='>=3.8',
    #include_package_data=True,
    #package_data=package_data,
)
