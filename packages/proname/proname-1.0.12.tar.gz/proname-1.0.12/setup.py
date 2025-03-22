import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proname",
    version="1.0.12",
    author="ZZL",
    url='https:\\www.baidu.com',
    author_email="test@163.com",
    description="first demo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,
    data_files=[('include', ['src/proname/include/VnHardwareConf.dll'])],
)