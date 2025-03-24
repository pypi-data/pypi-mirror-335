from setuptools import setup

setup(
    name='moonshotai_integration',
    packages=[
        'moonshotai_integration',
        'moonshotai_integration.utils'
    ],
    version='0.0.3',
    description='MoonshotAI Data Integration SDK',
    author='Tomer Efr',
    install_requires=[
        "requests==2.31.0",
        "pandas==1.4.4",
        "boto3==1.36.26"
    ],
    zip_safe=False,
    license='MIT',
    classifiers=[],
    package_data={'': ['LICENSE', 'README.md']}
)
