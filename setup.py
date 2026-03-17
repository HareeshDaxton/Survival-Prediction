from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements =[
        line.strip() 
        for line in f 
        if line.strip() and not line.startswith('#')
    ]
    
setup(
    name='Survival_prediction_mlops3',
    version='0.2',
    author='Hareesh Kumar',
    packages=find_packages(),
    package_data={              
        '': ['*.yaml', '*.json', '*.txt'],
    },
    install_requires=requirements
    
)