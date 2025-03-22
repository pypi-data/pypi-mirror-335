from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob
import os

# Dynamically find all .pyx files
pyx_files = glob.glob("*.pyx") + glob.glob("helpers/*.pyx")
print("Found .pyx files:", pyx_files)  # Debug print

setup(
    name="srswti-cython-windows",
    version="2.0.2",
    packages=find_packages(),
    ext_modules=cythonize(pyx_files, compiler_directives={'language_level': "3"}, build_dir="build"),
    install_requires=[
        "anthropic", "cerebras_cloud_sdk", "fastapi", "gcloud", "google-ai-generativelanguage",
        "google-api-core", "google-api-python-client", "google-auth", "google-auth-httplib2",
        "google-cloud-speech", "google-cloud-texttospeech", "google-genai", "google-generativeai",
        "googleapis-common-protos", "grpcio", "httpx", "jiter", "lxml", "nltk", "oauth2client",
        "openai", "packaging", "pillow", "postgrest", "PyAudio", "pydantic", "pydantic_core",
        "pydub", "pyinstaller", "python-dotenv", "redis", "regex", "requests", "starlette",
        "supabase", "tqdm", "uvicorn", "websockets",
    ],
    include_package_data=True,
    author="SRSWTI Inc.",
    author_email="team@srswti.com",
    description="A Cythonized package for srswti",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)