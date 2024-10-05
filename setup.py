from setuptools import setup

import warawara


setup(
    name='warawara',
    version=warawara.__version__,
    description='Some cute utilties for my other projects',
    author='Chang-Yen Chih',
    author_email='michael66230@gmail.com',
    url=f'https://github.com/pi314/warawara',
    py_modules=['warawara'],
    keywords=['warawara', 'utiliy', 'toolbox'],
    entry_points = {
        'console_scripts': [
            'wara=warawara:bin.warawara.main',
            'palette=warawara:bin.palette.main',
            'rainbow=warawara:bin.rainbow.main',
            'sponge=warawara:bin.sponge.main',
            'ntfy=warawara:bin.ntfy.main',
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
