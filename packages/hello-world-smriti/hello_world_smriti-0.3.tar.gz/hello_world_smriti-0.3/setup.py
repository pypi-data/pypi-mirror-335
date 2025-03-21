# from setuptools import setup, find_packages

# setup(
#     name ="hello_world",
#     version="0.1",
#     packages= find_packages(),
#     install_requires=[],
# )


from setuptools import setup, find_packages

setup(
    name ="hello_world_smriti",
    version="0.3",
    packages= find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hello_world = hello_world:hello"
        ]
    },
)