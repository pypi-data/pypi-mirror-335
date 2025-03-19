from setuptools import setup, find_packages

setup(
    name='telog',
    version='0.0.8',
    description='Telegram bot loger for django',
    author='Bahodir',
    author_email='weebcreator94@gmail.com',
    packages=find_packages(),
    install_requires=[
        'python-dotenv'
    ],
    python_requires='>=3.6',
)
