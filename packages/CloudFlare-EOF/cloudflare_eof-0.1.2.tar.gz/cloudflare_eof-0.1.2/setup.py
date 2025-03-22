from setuptools import setup, find_packages

setup(
    name="CloudFlare_EOF",
    version="0.1.2",
    author="Elxss",
    author_email="elxssgitcontact@gmail.com",
    description="CloudFlare_EOF is a project to decode email addresses protected and Obfuscated by Cloudflare.",
    url="https://github.com/Elxss/CloudFlare-Email-Obfuscation-Fucker",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
    ],
)