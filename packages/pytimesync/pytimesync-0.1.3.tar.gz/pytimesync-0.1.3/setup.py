from setuptools import setup, find_packages
DEPENDENCIES = []
setup(
    name='pytimesync',
    version='0.1.3',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    author='vk',
    author_email='vk123@gmail.com',
    description='A short description of your package',
     entry_points={"console_scripts": ["pytimesync=pytimesync.main:main"]},
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/vk/pytimesync',
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
