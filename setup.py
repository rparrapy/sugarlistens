from setuptools import setup

setup(
    name="sugarlistens",
    version="0.0.1",
    author="Rodrigo Parra",
    author_email="rodpar07@gmail.com",
    description=("Speech Recognition Project for the Sugar Learning Platform"),
    license="GPL",
    keywords="speech recognition sugar",
    packages=['sugarlistens'],
    package_data={'sugarlistens': ['../etc/*.conf', '../etc/*.service']}
)
