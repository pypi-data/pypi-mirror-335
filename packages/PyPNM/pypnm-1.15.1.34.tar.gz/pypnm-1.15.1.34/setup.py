import setuptools

with open('README.md') as file:
    read_me_md = file.read()

setuptools.setup(
    name='PyPNM',
    version='1.15.1.34',
    author='Ilya Razmanov',
    author_email='ilyarazmanov@gmail.com',
    description='Reading and writing PPM and PGM image files, including 16 bits per channel, in pure Python 3.4 and above',
    long_description=read_me_md,
    long_description_content_type='text/markdown',
    url='https://github.com/Dnyarri/PyPNM',
    packages=['pypnm'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Topic :: File Formats',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['ppm', 'pgm', 'pbm', 'pnm', 'Netpbm', 'image', 'bitmap', 'format', 'python'],
    python_requires='>=3.4',
)
