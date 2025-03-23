from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="cdt_path",
    version='2.3.0',
    author="CaiShu",
    author_email="caiyi@mail.ustc.edu.cn",
    description="Constrainted Delaunay Triangle for path-planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # license="MIT",
    # url="https://gitee.com/DerrickChiu/function_tool.git",
    packages=find_packages(),
    install_requires=[	'matplotlib',
						'triangle',
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
