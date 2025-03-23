from setuptools import setup, find_packages

setup(
    name="logninja-create-vm",
    version="0.1.2.dev0",
    description="Interactive CLI tool for provisioning virtual machines using virt-install (LOGGIE infrastructure)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="loggie.eth",
    author_email="founder@loggie.ai",
    url="https://github.com/loggie-eth/logninja-create-vm",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Emulators",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "logninja-create-vm = logninja_create_vm.cli:main"
        ]
    },
    include_package_data=True,
    python_requires='>=3.7',
    license="MIT",
)
