from setuptools import setup

setup(
    name='ecotrade',
    version='1.3',
    author='Zyber Pireci & Vishva Teja Janne',
    author_email='supporto@ecotrade.bio',
    description='An Ecotrade package to manage the software infrastructure',
    long_description='A detailed description of what the Ecotrade package does...',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ecotrade', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests', 'pyodbc'],
    python_requires='>=3.6',
    license='MIT', 
)
