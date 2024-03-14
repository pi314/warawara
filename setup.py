from setuptools import setup

import smol


setup(
    name='smol',
    version=smol.__version__,
    description='Some smol utilties for my other projects',
    author='Chang-Yen Chih',
    author_email='michael66230@gmail.com',
    url=f'https://github.com/pi314/smol',
    py_modules=['smol'],
    keywords=['smol', 'utiliy', 'toolbox'],
    entry_points = {
        'console_scripts': [
            'smol=smol:cli_smol.main',
            'palette=smol:cli_palette.main',
            'rainbow=smol:cli_rainbow.main',
            'sponge=smol:cli_sponge.main',
            'ntfy=smol:cli_ntfy.main',
            ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
