from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

VERSION = '0.0.3'
DESCRIPTION = 'A package to create image games and light novels'
LONG_DESCRIPTION = 'A package to create image games and light novels easily'

# Setting up
setup(
    
    name="imagegamepy",
    version=VERSION,
    author="WinnyCode (Etchike Hugues Winny Lyonnais)",
    author_email="<winnyblackstart@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['Pillow', 'pygame', 'numpy', 'keyboard', 'ffpyplayer'],
    keywords=['python', 'video game', 'Novel', 'game', 'image', 'image game'],
    license='Apache 2.0',
    url='https://github.com/winnyblackstart/imagegamepy.git',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requirement=">=3.6"
)
