from setuptools import setup, find_packages
with open('pyluno/meta.py') as f:
    exec(f.read())

setup(
    name='pyluno',
    version=__version__,
    packages=find_packages(exclude=['tests']),
    description='A Luno API for Python',
    author='Cayle Sharrock/Grant Stephens',
    author_email='grant@stephens.co.za',
    scripts=['demo.py'],
    install_requires=[
        'futures>=3.0.3',
        'nose>=1.3.7',
        'requests>=2.8.1',
        'pandas>=0.17.0',
    ],
    license='MIT',
    url='https://github.com/grantstephens/pyluno',
    download_url='https://github.com/grantstephens/pyluno/tarball/%s'
        % (__version__, ),
    keywords='Luno Bitcoin exchange API',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Office/Business :: Financial',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    extras_require={
        'test':  ['requests-mock>=0.7.0', 'nose'],
        }
)
