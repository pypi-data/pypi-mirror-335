from .print_fonts import PrintFonts

class ListAll():
    def __init__(self):
        pf = PrintFonts()
        text = """
        # Here you can find all the resources of the module:
        datascience = Data Science with Pandas, Plots with Matplotlib and Seaborn and Machine-Learning with Scikit-learn
        deeplearning = Deep Learning models with Tensorflow Keras
        telegrambot = Setup your own Telegram Bot with python-telegram-bot module
        django = Configure your Django backend and get some exaples for your applications
        cookiecutter = Quick-Start with a pre-configured Django project
        createpypimodule = Simple commands to create your own PyPi module
        ollama = Chat with an AI LLM model from Ollama directly in your Python code
        """
        pf.format(text)