from setuptools import setup, find_packages

setup(
    name='kybatis',
    version='0.0.2',
    license='Apache-2.0',
    description='minimal db utility in mybatis style',
    author='kyon',
    author_email='originky2@gmail.com',
    install_requires=['pydantic>=2.10', 'oracledb>=2.5', 'mysql-connector-python>=9.2',],
    packages=find_packages(exclude=[]),
    python_requires='>=3.10',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.11',
    ],
)
