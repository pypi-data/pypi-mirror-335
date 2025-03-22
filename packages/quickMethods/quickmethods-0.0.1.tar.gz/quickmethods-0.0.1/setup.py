from setuptools import setup, find_packages

#def long_description() -> str:
#    long_description: str = ''
#    with open('README.md', 'r', encoding='utf-8') as file:
#        long_description += file.read()
#    with open('CHANGELOG.md', 'r', encoding='utf-8') as file:
#        long_description += f'\n\n{file.read()}'
#    return long_description

setup(
    name='quickMethods',
    version='0.0.1',
    description='A simple library to make your life faster with quick methods!',
    #long_description=long_description(),
    long_description_content_type='text/markdown',
    author='Orly Neto',
    author_email='orly2carvalhoneto@gmail.com',
    license='MIT License',
    keywords=['useful'],
    packages=find_packages())