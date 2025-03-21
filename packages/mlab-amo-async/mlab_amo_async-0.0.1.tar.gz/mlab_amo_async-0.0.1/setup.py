from setuptools import setup

setup(
    name='mlab_amo_async',
    version='0.0.1',
    author='MLAB',
    install_requires=[
        'requests',
        'motor',
        'importlib-metadata; python_version<"3.11"',
    ],
)