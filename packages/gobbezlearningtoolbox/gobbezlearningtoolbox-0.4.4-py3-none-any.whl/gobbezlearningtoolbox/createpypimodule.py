from .print_fonts import PrintFonts


class CreatePyPiModule():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## CREATE YOUR PYPI MODULE
        ! Simple commands to create your own Python module.

        # Details:
        -details() = Get step-by-step details
        
        # Commands:
        -commands() = Commands to create your Python module
        """
        pf.format(text)

    def commands(self):
        """Commands to create your Python module"""
        pf = PrintFonts()

        text = """  
        ## SHELL COMMANDS

        ! Run this from the (venv) Python shell, in the folder that you want to use 
        $ pip install setuptools twine
        
        ! Run these from the (venv) Python shell, after your have configured your module and its code
        ! You must have a PyPi account and get its API_KEY. You can do so in the official PyPi website.
        python setup.py sdist bdist_wheel
        twine upload dist/*
        
        ! After everything is fine you can install your module from pip
        pip install my_package
        
        ! You can test it on a Python code
        from my_package.core import greet
        print(greet("Pythonista"))
        
        ! If you want to make updates in your module, simply delete the: build, dist and my_package.egg-info folders
        ! Update the setup.py file with the version number
        ! And run these in your (venv) Python shell
        python setup.py sdist bdist_wheel
        twine upload dist/*
        """
        pf.format(text)

    def details(self):
        """Details to create your Python module"""
        pf = PrintFonts()

        text = """  
        ## PROJECT FOLDER DETAILS
        
        # Here are the details of every file that you need to have to create your own PyPi module
        my_package/
        ├── my_package/
        │   ├── __init__.py
        │   ├── core.py
        ├── tests/
        │   ├── test_core.py
        ├── README.md
        ├── LICENSE
        ├── setup.py
        ├── pyproject.toml
        
        my_package/__init__.py = You can leave it blank. It's used to make it a Python package
        my_package/core.py = The code of your module. You can add as many Python files as you want
        tests/test_core.py = Tests for the code of your module
        README.md = Used for both Github (if possible) and your PyPi module page
        LICENSE = Optional licence of your module
        setup.py = Settings of your module
        pyproject.toml = Optional setting of the building tools
        
        ### setup.py
        # Example of the setup.py file
        from setuptools import setup, find_packages

        setup(
            name="my_package",
            version="0.1.0",
            author="Your name",
            author_email="your.email@example.com",
            description="Example Python module",
            long_description=open("README.md").read(),
            long_description_content_type="text/markdown",
            url="https://github.com/your_username/my_package",
            packages=find_packages(),
            classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
            ],
            python_requires=">=3.6",
        )

        ### pyproject.toml
        # Example of the pyproject.toml file
        [build-system]
        requires = ["setuptools", "wheel"]
        build-backend = "setuptools.build_meta"
        
        ### tests/test_core.py
        # Example of tests for your module
        import unittest
        from my_package.core import greet
        
        class TestGreet(unittest.TestCase):
            def test_greet(self):
                self.assertEqual(greet("World"), "Hello, World!")
                
        # Run this in your bash:
        $ python -m unittest discover
        """
        pf.format(text)