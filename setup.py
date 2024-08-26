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
            'smol=smol:bin.smol.main',
            'palette=smol:bin.palette.main',
            'rainbow=smol:bin.rainbow.main',
            'sponge=smol:bin.sponge.main',
            'ntfy=smol:bin.ntfy.main',
            ],
    },
    python_requires='>=3.7',
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
