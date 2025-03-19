from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='common_api_test_engine',
    version='1.1.1',
    author='dawnpopo',
    author_email='1916364638@qq.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Faker>=13.4.0",
                      "jsonpath>=0.82.2",
                      "pymysql>=1.1.1",
                      "requests-toolbelt>=0.9.1",
                      "rsa>=4.8"
                      ],
    packages=find_packages(),
    package_data={
        "": ["*.html", '*.md'],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
