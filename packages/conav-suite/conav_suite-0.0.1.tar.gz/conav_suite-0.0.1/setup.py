from setuptools import setup, find_packages

setup(
    name="conav_suite",
    version="0.0.1",
    packages=find_packages(),
    author="Ethan Clark",
    author_email="eclark715@gmail.com.com",
    description="A multi-agent environment inspired by the Lewis Signaling Game, featuring eight unique problem configurations with both static and dynamic obstacles.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/ethanmclark1/conav_suite",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
