from setuptools import setup, find_packages

setup(
    name="taya",  # اسم الحزمة
    version="0.1.0",
    author="IMAD-213",
    author_email="madmadimado59@gmail.com",
    description="FREE FIRE PAGE HACK",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/imadoo27/taya",  # رابط المستودع (اختياري)
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "taya=taya.runner:main",  # ربط السكربت بـ CLI
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
