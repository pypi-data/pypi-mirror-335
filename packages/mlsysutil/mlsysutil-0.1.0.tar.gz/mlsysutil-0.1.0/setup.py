from setuptools import setup, find_packages

setup(
    name="mlsysutil",  # 패키지명 (변경 가능)
    version="0.1.0",  # 버전
    author="texnee",
    author_email="texnee@gmail.com",
    description="A package for AI System Utils",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jelite/mlsysUtils",  # GitHub 또는 프로젝트 URL
    packages=find_packages(),  # mypackage/ 폴더를 패키지로 포함
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 최소 요구 Python 버전
    install_requires=[],  # 의존 패키지 (예: ["numpy", "matplotlib"])
)