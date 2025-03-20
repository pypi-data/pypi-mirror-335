"""
Setup script for json_graph_traversal package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="json_graph_traversal",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package to traverse nested JSON data structures using BFS or DFS algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prajak002/json_graph_traversal",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    keywords="json, graph, traversal, bfs, dfs, search",
)