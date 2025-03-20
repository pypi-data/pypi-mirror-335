from setuptools import setup, find_packages

setup(
    name="flask-mvc-core",
    version="0.1.2",
    description="Wrapper personalizado para Flask com estrutura MVC",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Célio Junior",
    author_email="profissional.celiojunior@outlook.com",
    url="https://github.com/celiovmjr/flask-mvc-core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=['Flask>=3.0.0', 'waitress'],
)
