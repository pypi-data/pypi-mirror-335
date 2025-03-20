from setuptools import setup, find_packages

setup(
    name="mkdocs-hr-plugin",
    version="0.1.0",
    author="amaranth",
    author_email="amaranth2082@gmail.com",
    description="A MkDocs plugin that converts text between triple dashes to HR elements",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Auzers/mkdocs-hr-plugin",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        'mkdocs_hr_plugin': ['assets/*.js', 'assets/*.css'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mkdocs>=1.0.0",
    ],
    entry_points={
        'mkdocs.plugins': [
            'upgradehr = mkdocs_hr_plugin:HRPlugin',
        ]
    },
    use_scm_version=True,  # 自动管理版本号
)
