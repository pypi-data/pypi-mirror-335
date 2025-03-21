import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setuptools.setup(
    name='nyxara',
    version='0.1',
    author='nyxara',
    description='data analysis utils',
    long_description=readme,
    long_description_context_type='text/markdown',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[]
    )
