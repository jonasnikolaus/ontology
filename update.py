import os

with open('requirements.txt', 'r') as file:
    packages = file.readlines()

for package in packages:
    package = package.split('==')[0]
    os.system(f'pip install --upgrade {package}')