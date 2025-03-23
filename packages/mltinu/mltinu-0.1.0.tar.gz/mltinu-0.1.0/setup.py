from setuptools import setup, find_packages

setup(
    name='mltinu',  # Replace with your package name.
    version='0.1.0',
    description='A package that generates machine learning pipeline code using LangChain and ChatOpenAI.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Tinu',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/my_package',  # Replace with your repository URL.
    packages=find_packages(),
    install_requires=[
        'pandas',
        'langchain_openai',  # Add any other dependencies.
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update if using a different license.
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
