# from setuptools import setup, find_packages

# setup(
#     name ="hello_world",
#     version="0.1",
#     packages= find_packages(),
#     install_requires=[],
# )


# from setuptools import setup, find_packages

# setup(
#     name ="hello_world_smriti",
#     version="0.3",
#     packages= find_packages(),
#     install_requires=[],
#     entry_points={
#         "console_scripts": [
#             "hello_world_smriti = hello_world:hello"
#         ]
#     },
# )


from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name ="hello_world_smriti",
    version="0.4",
    packages= find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hello_world_smriti = hello_world:hello"
        ]
    },
    long_description = description,
    long_description_content_type= "text/markdown",
)