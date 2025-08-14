from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "A professional URL shortener service built with Flask"

# Read requirements
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return [
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "gunicorn==21.2.0",
        "python-dotenv==1.0.0",
    ]

setup(
    name="url-shortener",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A professional URL shortener service with modern web interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/url-shortener",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.10.0",
        ],
        "prod": [
            "gunicorn>=21.0.0",
            "nginx>=1.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "url-shortener=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/*", "*.md", "*.txt", "*.yml", "*.yaml"],
    },
    data_files=[
        ("config", ["docker-compose.yml", "nginx.conf", "Dockerfile"]),
        ("deployment", ["railway.toml", "vercel.json", "render.yaml", "fly.toml", "app.yaml"]),
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/url-shortener/issues",
        "Source": "https://github.com/yourusername/url-shortener",
        "Documentation": "https://github.com/yourusername/url-shortener#readme",
    },
)