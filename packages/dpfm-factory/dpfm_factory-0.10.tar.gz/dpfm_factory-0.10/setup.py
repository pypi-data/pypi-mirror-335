from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

def parse_requirements(filename):
    req_path = os.path.join(here, filename)
    with open(req_path, 'r') as file:
        return [line.strip() for line in file if not line.startswith("git+") and line.strip()]

def parse_dependency_links(filename):
    req_path = os.path.join(here, filename)
    with open(req_path, 'r') as file:
        return [line.strip() for line in file if line.startswith("git+")]

setup(
    name="dpfm_factory",
    version="0.10",
    author="Steven N. Hart",
    author_email="Hart.Steven@Mayo.edu",
    description="Helper scripts for digital pathology foundation models",
    long_description=open(os.path.join(here, 'README.md')).read(),
    long_description_content_type="text/markdown",  # Specify that README is in Markdown
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    dependency_links=parse_dependency_links('requirements.txt'),
    include_package_data=True,
    package_data={
        'dpfm_model_runners': ['data/macenko_target.png'],  # Explicitly include specific data files
    },
)
