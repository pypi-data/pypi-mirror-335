from setuptools import setup, find_packages

setup(
    name='subpr',
    version='0.0.4',
    description='subprocess.run & os.chdir python shell libs (shell/exec/load/compile)',
    author='du7ec',
    author_email='dutec6834@gmail.com',
    url='https://github.com/FarAway6834/SubprunShell',
    packages=find_packages(exclude=[]),
    install_requires=['martialLaw',],
    keywords=['subpr'],
    python_requires='>=3.6',
    package_data={},
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
)
