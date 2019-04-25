from setuptools import setup, find_packages
import tcapi

setup(
    name="T&C API",
    version=tcapi.__version__,

    description="Terms & Conditions Web API",
    long_description="Terms & Conditions Web API",
    url="https://github.com/imec-ilabt/terms-cond-demo-site",

    packages=find_packages(exclude=["doc"]),

    entry_points={
        "console_scripts": [
            "tcapi=tcapi.tc_api_app:main"
        ]
    },

    author="Wim Van de Meerssche",
    author_email="wim.vandemeerssche@ugent.be",
    license="MIT",

    python_requires='>=3.6',

    install_requires=["flask>=1.0.2", "python-dateutil>=2.7.3", "flask-cors", "pytz", "cryptography"],
    dependency_links=[],

    setup_requires=[],
    tests_require=[]
)
