from setuptools import setup, find_packages

setup(
    name='contract-ai-agent',
    version='0.1.0',
    packages=find_packages(where='.', include=['contract_ai_agent_modules*']),
    include_package_data=True,
    package_data={
        'contract_ai_agent_modules': ['static/images/*.svg'],
    },
    install_requires=[
        'google-cloud-bigquery',
        'typing_extensions',
        'streamlit',
        'cairosvg',
        'Pillow',
    ],
)