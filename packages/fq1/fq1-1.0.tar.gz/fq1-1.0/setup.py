from setuptools import setup, find_packages



setup(
    name="fq1",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "install-github=FQ.auto_install:install_github_repo",
        ],
    },
    author="NgocAn",
    author_email="anlam9614@gmail.com",
    description="Thư viện tự động tải về GitHub repo",
    url="https://github.com/NgocAnLam/fqtest.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)