from setuptools import setup, find_packages

setup(
    name='snp_manager', 
    version='0.1.2', 
    author='Shashank Rao',
    author_email='shashankrao.websites@gmail.com',
    description='Read the README',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ShashankRaoCoding/SNP_Manager',
    packages=find_packages(),
    license = "LGPL-3.0-or-later" , 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
