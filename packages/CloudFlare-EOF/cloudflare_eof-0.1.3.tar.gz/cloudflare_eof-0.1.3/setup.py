from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    description_s = f.read()

setup(
    name="CloudFlare_EOF",
    version="0.1.3",
    author="Elxss",
    author_email="elxssgitcontact@gmail.com",
    description="CloudFlare_EOF is a project to decode email addresses protected and Obfuscated by Cloudflare.",
    url="https://github.com/Elxss/CloudFlare-Email-Obfuscation-Fucker",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
    ],
    long_description=description_s,
    long_description_content_type="text/markdown"
)