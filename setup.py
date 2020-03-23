import pathlib
import setuptools


setuptools.setup(
    name='panda3d-kivy',
    version='0.1.1',
    author='Cheaterman',
    author_email='the.cheaterman@gmail.com',
    description='Panda3D add-on for Kivy integration.',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/Cheaterman/panda3d-kivy',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.6',
    install_requires=['panda3d', 'kivy'],
)
