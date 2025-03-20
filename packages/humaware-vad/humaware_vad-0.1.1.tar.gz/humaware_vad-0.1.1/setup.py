from setuptools import setup, find_packages
import os
# print(os.getcwd())
def read_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]
setup(
    name="humaware-vad",
    version="0.1.1",
    author="Sourabh Saini",
    author_email="Sourabh72101@gmail.com",
    description="HumAwareVAD: A optimized voice activity detection model to better distinguish humming and speech",
    url="https://github.com/CuriousMonkey7/humaware-vad",  # Replace with actual URL
    packages=find_packages(),
    install_requires= read_requirements(),
    include_package_data=True,  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.12",
)
