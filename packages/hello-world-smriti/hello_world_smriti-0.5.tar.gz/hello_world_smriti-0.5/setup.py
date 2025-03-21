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


# from setuptools import setup, find_packages

# with open('README.md', 'r') as f:
#     description = f.read()

# setup(
#     name ="hello_world_smriti",
#     version="0.4",
#     packages= find_packages(),
#     install_requires=[],
#     entry_points={
#         "console_scripts": [
#             "hello_world_smriti = hello_world:hello"
#         ]
#     },
#     long_description = description,
#     long_description_content_type= "text/markdown",
# )


from setuptools import setup, find_packages

# Read README.md for the long description
with open("README.md", "r", encoding="utf-8") as f:  # Ensure UTF-8 encoding
    long_description = f.read()

setup(
    name="hello_world_smriti",
    version="0.5",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hello_world_smriti=hello_world:hello"
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,  # Ensure README.md is included
)
