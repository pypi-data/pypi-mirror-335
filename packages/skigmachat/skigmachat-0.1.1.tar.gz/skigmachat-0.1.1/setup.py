from setuptools import setup, find_packages

setup(
    name='skigmachat',
    version='0.1.1',
    packages=find_packages(),
    install_requires=['websockets'],
    author='Spigey',
    author_email='ludwig@skigmanetwork.de',
    description='Discord bot for chatroom.skigmanetwork.de',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Spigey/skigmachat',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
