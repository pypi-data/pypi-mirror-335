import setuptools

setuptools.setup(
    name="streamlit-image_uploader",
    version="0.0.2",
    author="John Sebastián Galindo Hernández",
    author_email="johnsgalindo@ucundinamarca.edu.cos",
    description="This is a streamlit component that allows you to upload images, its component was made for change the text to whatever lenguage you want.",
    long_description="the component receives the following parameters: buttonText, dropText, allowedFormatsText, borderColor, buttonColor, buttonTextColor, hoverButtonColor, key. The component returns a dict with the fileName of the image uploaded and its preview",
    long_description_content_type="text/plain",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.12",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 1.43.2",
    ],
    extras_require={
        "devel": [
            "wheel",
            ]
    }
)