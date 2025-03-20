class PrintFonts():
    def format(self, text):
        """Format the text
        ## = title
        # = comment (green)
        else = code (blue) or blank line
        """
        for row in text.split("\n"):
            # Remove starting spaces
            stripped_row = row.lstrip()

            if stripped_row.startswith("##"):
                print(self.use_title(stripped_row[2:]+" "))
            elif stripped_row.startswith("#"):
                print("#" + self.add_color(stripped_row[1:], "green"))
            elif stripped_row.startswith("!"):
                print(stripped_row[1:])
            elif stripped_row:
                print(self.add_color(stripped_row, "blue"))
            else:
                # Write a blank line
                print("")


    def use_title(self, text):
        """Use color red and - -"""
        text = self.add_title(text=text)
        text = self.add_color(text=text, color="red")
        return text

    def add_color(self, text="", color="red"):
        """Create colored prints!"""
        colors = {
            "red": "\033[1;31m",
            "blue": "\033[1;34m",
            "green": "\033[1;32m"
        }

        return f"{colors.get(color, '')}{text}\033[0m" if color in colors else text

    def add_title(self, text=""):
        """Put the text between - -"""
        return "-" * 10 + text + "-" * 10

