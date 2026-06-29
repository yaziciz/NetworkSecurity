from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    """
    This function will return the list of requirements
    """
    requirements_list:List[str] = []
    try:
        with open("requirements.txt") as requirements_file:
            requirements_list = requirements_file.readlines()
            for index, requirement in enumerate(requirements_list):
                requirements_list[index] = requirement.strip()
                if requirement and requirement.startswith("-e"):
                    requirements_list[index] = requirement.split("=")[-1]
    except Exception as e:
        print(f"Error reading requirements.txt: {e}")
    return requirements_list

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Ziya Ata Yazici",
    packages=find_packages(),
    install_requires=get_requirements()
)
    

    