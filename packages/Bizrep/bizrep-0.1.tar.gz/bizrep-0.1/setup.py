from setuptools import setup, find_packages

setup(
    name="Bizrep", 
    version="0.1", 
    author="karisham m patel",  
    author_email="karishma2o@gmil.com",  
    description="A Python library for predictive analytics and business forecasting.", 
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",  
    url="https://github.com/MOON11kr/Bizrep",
    packages=find_packages(), 
    install_requires=[  # List of dependencies
        "pandas",
        "scikit-learn",
        "prophet",
        "statsmodels",
        "reportlab",
        "openpyxl",
        "plotly",
        "dash",
    ],
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
)
