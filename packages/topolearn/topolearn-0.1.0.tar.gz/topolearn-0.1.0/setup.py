from setuptools import setup, find_packages

setup(
    name='topolearn',
    version='0.1.0',
    description='Topolearn score computed using persistent homology',
    url='https://github.com/Boehringer-Ingelheim/topolearn',
    author='Florian Rottach',
    author_email='florianrottach@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['numpy==1.26.4',
                      'ripser==0.6.8',
                      'giotto-tda==0.6.0',
                      'pandas==2.0.0',
                      'scikit-learn==1.5.1'],
    include_package_data=True,
    package_data={
        'topolearn': ['topolearn.pkl'],
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
    ],
)
