from setuptools import setup, find_packages

setup(
    name='lessllm',
    version='0.0.2',
    author='simpx',
    author_email='simpxx@gmail.com',
    description='A lightweight framework for LLM inference',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/simpx/lessllm',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'transformers',
        'torch',
        'requests>=2.20.0,<3.0.0',
        'urllib3>=1.25.4,<2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'lessllm=lessllm.model:main',
        ],
    },
)
