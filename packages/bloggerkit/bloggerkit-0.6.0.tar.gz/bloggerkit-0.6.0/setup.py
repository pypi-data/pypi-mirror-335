from setuptools import find_packages, setup

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A toolkit for interacting with the Google Blogger API"

setup(
    name='bloggerkit',
    version='0.5.0',
    packages=find_packages(),
    install_requires=[
    ],
    author='StatPan Lab',
    author_email='statpan@naver.com',
    description='A toolkit for interacting with the Google Blogger API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/StatPan/bloggerkit',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)