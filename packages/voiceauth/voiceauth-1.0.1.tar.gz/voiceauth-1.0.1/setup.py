import os
from setuptools import setup, find_packages

# Read requirements from file
with open('VoiceAuth/requirements.txt') as f:
    requirements = f.read().splitlines()
    # Remove comments and empty lines
    requirements = [line for line in requirements if line and not line.startswith('#')]

# Process requirements to ensure scikit-learn uses binary wheels
processed_requirements = []
for req in requirements:
    if req.startswith("scikit-learn=="):
        # Keep any environment markers for scikit-learn
        if ";" in req:
            base, marker = req.split(";", 1)
            processed_requirements.append(f"{base.strip()};{marker.strip()}")
        else:
            processed_requirements.append(req)
    else:
        processed_requirements.append(req)

# Read the long description from README
with open('VoiceAuth/README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="voiceauth",
    version="1.0.1",
    author="Zohaib Lazuli",
    author_email="zohaibkhanbhs@gmail.com",  # Updated with user's email
    description="AI Voice Detection System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zohaiblazuli/VoiceAuth",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=processed_requirements,
    include_package_data=True,
    package_data={
        'VoiceAuth': [
            'media/*',
            'output/.gitkeep',
            'samples/.gitkeep',
        ],
    },
    entry_points={
        'console_scripts': [
            'voiceauth=VoiceAuth.run_voiceauth:main',
        ],
    },
) 