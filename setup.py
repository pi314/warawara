from setuptools import setup

import nano


setup(
    name='nano',
    version=nano.__version__,
    description='Some nano-sized utilties for my other projects',
    author='Chang-Yen Chih',
    author_email='michael66230@gmail.com',
    url=f'https://github.com/pi314/nano',
    py_modules=['nano'],
    keywords=['nano', 'utiliy', 'toolbox'],
    entry_points = {
        'console_scripts': [
            'nano=nano:cli_main.main',
            'palette=nano:cli_palette.main',
            'rainbow=nano:cli_palette.main',
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
