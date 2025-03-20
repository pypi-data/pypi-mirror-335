from .print_fonts import PrintFonts


class Ollama():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## USE OLLAMA AI LLM MODELS
        ! Start with simple but powerful AI LLM models

        # Imports:
        -imports() = Ollama imports
        
        # Commands: 
        -commands() = Ollama shell commands to install a model

        # Chat:
        -chat() = Example code to configure and use a LLM model
        """
        pf.format(text)

    def imports(self):
        """Imports to use Ollama on your Python code"""
        pf = PrintFonts()

        text = """  
        ## OLLAMA IMPORTS
        import ollama
        """
        pf.format(text)

    def commands(self):
        """Commands to download and use Ollama and its models"""
        pf = PrintFonts()

        text = """  
        ## OLLAMA SHELL COMMANDS

        ! First of all install Ollama from its official website
        ! Search for a model that you want to use
        ! Run this from the Ollama shell (in this example i've used gemma3:4b)
        $ ollama run gemma3:4b
        """
        pf.format(text)

    def chat(self):
        """Example of a Python code to chat with your model"""
        pf = PrintFonts()

        text = """  
        ## OLLAMA CHAT

        # An example of a Python code to use your model
        # Select the model, the text to pass and the bot will generate an answer.
        # :param role: generally use 'user'. 'admin' gives other answers.
        # :param content: the message
        # :param model: the model to use
        # :return: the whole answer
        def stream_message(role, content, model):
            stream = ollama.chat(
                model=model,
                messages=[{'role': role, 'content': content}],
            )
            return stream['message']['content']
        """
        pf.format(text)