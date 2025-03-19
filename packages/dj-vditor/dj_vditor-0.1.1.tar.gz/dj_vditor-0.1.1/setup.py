from setuptools import setup, find_packages

setup(
    name="dj_vditor",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["Django >=3.2", "oss2 >=2.15.0; extra == 'oss'"],
    extras_require={"oss": ["oss2 >=2.15.0"]},
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
