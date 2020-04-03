from setuptools import setup, find_packages


SHORT_DESCRIPTION = 'Command-line tool to describe and visualize architecture schemes.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='archeme',
    version='1.0.2',
    url='https://github.com/foliant-docs/archeme',
    download_url='https://pypi.org/project/archeme',
    license='MIT',
    author='Artemy Lomov',
    author_email='artemy@lomov.ru',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'PyYAML>=5.1.1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points={
        'console_scripts': [
            'archeme=archeme:entry_point'
        ]
    }
)
