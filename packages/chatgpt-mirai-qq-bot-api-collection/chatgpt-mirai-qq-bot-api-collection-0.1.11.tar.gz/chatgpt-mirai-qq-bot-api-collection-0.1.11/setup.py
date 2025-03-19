from setuptools import setup, find_packages
import io
import os

version = os.environ.get('RELEASE_VERSION', '0.1.11'
'').lstrip('v')

setup(
    name="chatgpt-mirai-qq-bot-api-collection",
    version=version,
    packages=find_packages(),
    include_package_data=True,  # 这行很重要
    package_data={
        "api_collection": ["example/*.yaml", "example/*.yml"],
    },
    install_requires=["brotli","beautifulsoup4","html5lib"
    ],
    entry_points={
        'chatgpt_mirai.plugins': [
            'api_collection = api_collection:ApiCollectionPlugin'
        ]
    },
    author="chuanSir",
    author_email="416448943@qq.com",

    description="ApiCollectionPlugin for lss233/chatgpt-mirai-qq-bot",
    long_description=io.open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chuanSir123/api_collection",
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU Affero General Public License v3',
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/chuanSir123/api_collection/issues",
        "Documentation": "https://github.com/chuanSir123/api_collection/wiki",
        "Source Code": "https://github.com/chuanSir123/api_collection",
    },
    python_requires=">=3.8",
)
