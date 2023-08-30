from distutils.core import setup
setup(
    name = 'comdinheiro',
    packages = ['comdinheiro'],
    version = '0.1.6',
    license='GNU General Public License v2 (GPLv2)',
    description = "Interact with comdinheiro's API",
    author = 'Thomas Yasuoka',
    author_email = 'thomas.yasuoka@outlook.com',
    url = 'https://github.com/thomas-yasuoka/comdinheiro',
    download_url = "https://github.com/thomas-yasuoka/comdinheiro/archive/refs/tags/v0.1.6.tar.gz",
    keywords = ['api', 'comdinheiro'],
    install_requires=[
          'requests',
          "numpy",
          "pandas",
      ],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    ],
)
