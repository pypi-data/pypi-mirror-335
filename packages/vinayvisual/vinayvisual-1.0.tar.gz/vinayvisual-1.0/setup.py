from setuptools import setup,find_packages

setup(
    name='vinayvisual' , version='1.0' , packages=find_packages(),install_requires=['numpy','opencv-python','scipy'],author='vinaychouhan' ,
    long_description=open("README.md").read(),long_description_content_type='text/markdown' , url='https://github.com/vinaychouhan24/vinayvisual'
)