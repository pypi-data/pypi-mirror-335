from setuptools import setup, find_packages

setup(
    name='groclake',  # Name of the package
    version='0.2.7',
    packages=find_packages(),
    namespace_packages=['groclake'],  # Declare the namespace
    install_requires=[
        'requests',  # For HTTP requests
        'mysql-connector-python',  # For MySQL connection
        'redis',  # For Redis connection
        'elasticsearch>=8.11.0,<9.0.0',  # For Elasticsearch connection
        'google-cloud-storage',  # For GCP Storage interaction
        'Pillow',  # For image processing (PIL)
        'boto3',  # For AWS S3 interaction
        'pymongo',  # For MongoDB connection
        'PyPDF2',
        'markdownify',
        'python-docx',
        'google-genai',
        'openai',
        'anthropic',
        'google-generativeai',
        'groq',
        'pytz',
        'python-dotenv',
        'notion-client',
        'pypdf',
        'snowflake-connector-python', 
        'slack-sdk',
        'jira',
        'simple-salesforce'
    ],
)
