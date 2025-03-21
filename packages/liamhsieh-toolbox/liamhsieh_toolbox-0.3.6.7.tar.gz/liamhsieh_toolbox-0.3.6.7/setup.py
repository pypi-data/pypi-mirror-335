# Steps for updating this package
# 1. check files includes private/security info and make sure set .gitignore correctly
# 2. update markdown document associated to changes, index.md within python modules
# 3. update README.md, toolbox/change_log.md
# 4. update setup.py, set a new version number, check if any python package is required by changes and add into the file content
# 5. delete old archived files under <toolbox-project-directory>/dist/
# 6. create new archive files for this ditrtibution
#   #install or upgrade the setuptools and wheel packages in the user's home directory
#   python3 -m pip install --user --upgrade setuptools wheel 
#   #create archive files (could be found in folder dist/)
#   python3 setup.py sdist bdist_wheel
# 7. upload the archives to PyPi (login to Pypi and generate API tocken if not on hand)
#   #Check that pacakge twine has been installed
#   python3 -m pip install --user --upgrade twine 
#   twine upload dist/* 
# 8. test new distribution via pip install liamhsieh-toolbox
# 9. push all changes to Github

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="liamhsieh_toolbox",
    version = '0.3.6.7',
    description = "Collections of Python utility",
    author = 'Liam Y. Hsieh, PhD',
    author_email = 'liamhsieh@ieee.org',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    project_urls={
        'Homepage': 'https://github.com/liam-hsieh/liamhsieh-toolbox',
        'Docs':'https://liam-hsieh.github.io/liamhsieh-toolbox/'
    },
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
    ],
    #packages = ['toolbox'], #, since I only have a subfolder, toolbox, below setup.py and I don't wanna include docs as well, I just manually list what I need  
    python_requires='>=3.10',
    install_requires=[
        'pandas>=2.2',
        'sqlalchemy>=2.0',
        'openpyxl>=3.0.10',
        'xlsxwriter>=3.2.0',
        'pyxlsb>=1.0.9',
        'dask>=2024.5.0',
        'filetype>=1.1.0',
        'cx-Oracle>=8.3.0',
        'pyodbc>=4.0.0',
        'scipy>=1.9.0',
        'scikit-learn>=1.1.2',
        'matplotlib>=3.6.0',
        'pympler>=1.0.0',
        'pyarrow>=9.0.0',
        'streamlit>=1.13.0',
        'streamlit-drawable-canvas>=0.9.2',
        'streamlit-aggrid>=0.3.3',
        'azure-storage-blob>=12.14.0',
        'pymysql>=1.1',
        'pipe',
        'snowflake-sqlalchemy'
    ]
)
