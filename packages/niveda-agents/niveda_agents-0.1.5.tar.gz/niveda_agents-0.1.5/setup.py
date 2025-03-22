from setuptools import setup, find_packages

setup(
    name="niveda_agents",
    version="0.1.5",
    author="Sai Krishna Alle",
    author_email="saikrishnaalle1@gmail.com",
    description="A multi-agent AI framework integrating databases & AI platforms.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "psycopg2",                # PostgreSQL integration
        "pymongo",                 # MongoDB integration
        "openai",                  # OpenAI/Groq API
        "azure-ai-textanalytics",  # Azure OpenAI integration
        "transformers",            # Hugging Face models
        "fastapi",                 # API framework
        "uvicorn",                 # ASGI server for FastAPI
        "pytest",                  # Testing framework
        "python-dotenv",           # Environment variables
        "click",                   # CLI
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
