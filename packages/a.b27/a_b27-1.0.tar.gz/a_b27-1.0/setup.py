from setuptools import setup, find_packages

setup(
    name="a.b27",  # اسم المكتبة
    version="1.0",    # رقم الإصدار
    description="IMAD-213 Instagram Followers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="IMAD-213",
    author_email="madmadimado59@gmail.com",
    url="https://github.com/imadoo27/imad213-a.b27",
    packages=find_packages(),
    install_requires=[],  # ضع هنا المتطلبات إن وجدت
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
