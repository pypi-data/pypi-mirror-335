from setuptools import setup, find_packages

setup(
    name="dj-image-uploader-widget",
    version="0.4.5",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django>=4.0", "oss2>=2.15.0"],
    description="Django OSS Image Upload Widget with Customizable Configuration",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/ren000thomas/dj-image-uploader-widget",
    author="Ren Thomas",
    author_email="ren000thomas@gmail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
