import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="nonebot_plugin_emojilike_automonkey",
    version="0.0.1",
    author="BG4JEC",
    author_email="BG4JEC@hotmail.com",
    description="Nonebot2 emoji-monkey-like plugin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/2580m/nonebot-plugin-emojilike-automonkey",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)