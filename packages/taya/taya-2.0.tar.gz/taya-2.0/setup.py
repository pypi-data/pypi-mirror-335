from setuptools import setup, find_packages

setup(
    name="taya",
    version="2.0",
    author="IMAD-213",
    author_email="madmadimado59@gmail.com",
    description="Free Fire Page Hack",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/imadoo27/taya",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "taya": ["wz.py", "runner.py"],  # تضمين الملفات الثلاثة
    },
    entry_points={
        "console_scripts": [
            "taya=taya.runner:main",  # تشغيل runner.py عند استدعاء taya
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
