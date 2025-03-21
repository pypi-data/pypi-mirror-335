from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='XRP_converter',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'numpy',
        'tqdm',
        'matplotlib',
        'scikit-learn',
        'flask',
        'beautifulsoup4',
        'pytest',
        'pydantic',
        'asyncio'
    ],
    entry_points={
        'console_scripts': [
            'xrp_convert=xrp_converter.xrp_w_convert:main'
        ]
    },
    description='A cool XRP conversion library with extra tools.',
    author='kakz',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8'
)
