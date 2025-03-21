import os
from setuptools import setup, find_packages

setup(
    name='pscript',
    version='0.3.0',
    author='John Lam',
    author_email='jflam@microsoft.com',
    description='A library for writing LLM prompts as Python functions',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/jflam/pscript',
    packages=find_packages(include=['pscript', 'pscript.*']),
    install_requires=[
        'openai>=1.62.0',
        'anthropic>=0.45.2',
        'google-genai>=1.2.0',
        'pytest>=8.3.4',
        'filelock>=3.17.0',
        'pyyaml>=6.0.2',
        'pillow>=11.1.0',
        'tenacity>=9.0.0',
        'pytest-cov>=6.0.0',
        # Needed only to run the examples and example tests
        # 'datasets>=3.2.0',
        # 'e2b-code-interpreter>=1.0.5'
    ],
    entry_points={
        'console_scripts': [
            'pscript=pscript.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    include_package_data=True,
    package_data={
        'pscript': ['promptscript-defaults.yml'],
    },
)