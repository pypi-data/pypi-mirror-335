from setuptools import setup

setup(
    name='bloggerkit',
    version='0.1.0',
    packages=['.'],
    install_requires=[
    ],
    author='StatPan Lab',
    author_email='statpan@naver.com',
    description='A toolkit for interacting with the Google Blogger API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/StatPan/bloggerkit',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)