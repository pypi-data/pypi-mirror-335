from setuptools import setup, find_packages

setup(
    name="gnc",
    version="1.0.2",
    packages=find_packages(),
    package_data={"gnc": ["_gnc.pyd", "opencv_world4100.dll"]},
    include_package_data=True,
    python_requires="==3.12.*",
    install_requires=["opencv-python==4.10.0.84", "numpy==1.26.4", "setuptools>=76.0.0"],
    description="Custom Correlation tracker.",
    author="Oleksii Hospodarchuk; Denys Kolesnyk",
    author_email="olexago@ukr.net; kolesnik.d.i@gmail.com",
    url="https://github.com/kolesnikdi/corr_tracker",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
