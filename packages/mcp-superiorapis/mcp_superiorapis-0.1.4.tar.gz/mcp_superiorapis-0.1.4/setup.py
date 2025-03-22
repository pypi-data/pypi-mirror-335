from setuptools import setup, find_packages

setup(
    name='mcp-superiorapis',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pydantic',
        'fastmcp',
    ],
    python_requires='>=3.8',
    author='Marcus',
    description='MCP Server for SuperiorAPIs UVX platform',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo-link',
    entry_points={
        'console_scripts': [
            'mcp-superiorapis = mcp_server.main:main'
        ],
    },    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)