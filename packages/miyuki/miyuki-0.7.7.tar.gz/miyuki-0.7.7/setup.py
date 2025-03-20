from setuptools import setup, find_packages

setup(
    name='miyuki',
    version='0.7.7',
    packages=find_packages(),
    install_requires=[
        'curl_cffi',
    ],
    entry_points={
        'console_scripts': [
            'miyuki=miyuki.main:main',
        ],
    },
    python_requires='>=3.9',
)
