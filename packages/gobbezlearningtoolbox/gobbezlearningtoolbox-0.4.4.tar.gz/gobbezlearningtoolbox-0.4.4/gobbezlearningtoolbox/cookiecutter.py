from .print_fonts import PrintFonts


class CookieCutter():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## COOKIECUTTER
        ! Simple commands for Cookiecutter module.
        # Cookiecutter is a Python module that build pre-configurated projects (like Django projects)

        # Commands:
        -commands() = Cookiecutter commands
        """
        pf.format(text)

    def commands(self):
        """Cookiecutter commands"""
        pf = PrintFonts()

        text = """  
        ## IMPORTANT COOKIECUTTER SHELL COMMANDS

        ## EXAMPLE PRE-CONFIGURATED DJANGO READY-TO-GO PROJECT
        ! Run this from the (venv) Python shell, in the folder that you want to use 
        $ pip install cookiecutter
        $ cookiecutter gh:pydanny/cookiecutter-django
        ! Select the settings you want (like Docker or PostgreSql)
        """
        pf.format(text)