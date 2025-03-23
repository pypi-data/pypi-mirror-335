from setuptools import setup, find_packages

setup(
    name="conav_suite",
    version="0.0.2",
    packages=find_packages(),
    author="Ethan Clark",
    author_email="eclark715@gmail.com.com",
    description="A problem suite focused on evaluating the ability of autonomous agents to develop emergent communication strategies in cooperative navigation tasks",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/ethanmclark1/conav_suite",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
