from setuptools import setup, find_packages

setup(
    name='elkmlp',                
    version='0.2',                
    packages=find_packages(),     
    install_requires=[             
        'numpy',                  
    ],
    description='My homebrewed MLP library', 
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',  
    author='Leonid Elkin',   
    author_email='lnd.elkn@gmail.com', 
    url='https://github.com/Leonid-Elkin',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
)
