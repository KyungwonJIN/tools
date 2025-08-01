from setuptools import setup, find_packages

setup(
    name="kwtools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",  # CLI 인터페이스를 위한 패키지
        "tqdm>=4.65.0",   # 진행바 표시
        "pandas>=1.5.0",  # 데이터 처리
        "pillow>=9.0.0",  # 이미지 처리
    ],
    entry_points={
        'console_scripts': [
            'kwtools=kwtools.cli:main',
        ],
    },
    author="KW Jin",
    description="Utility tools for file and data management",
    python_requires=">=3.7",
)