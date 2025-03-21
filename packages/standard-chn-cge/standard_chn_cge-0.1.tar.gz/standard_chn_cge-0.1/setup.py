from setuptools import setup, find_packages

setup(
    name='standard_chn_cge',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            'run_project=Code.Run:main',
        ],
    },
    include_package_data=True,
    description="This model is a simplified version of a CGE model for China, including 2-factor inputs, 3 sectors, 2 final consumers, investment/saving account and global trade.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Junxi Qu (HKU)',
    author_email='qujunxi@connect.hku.hk',
    url='https://junexqu.github.io/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)