class Experiments:
    def __init__(self):
        self.codes = [
            """# Code Snippet 1\nprint("Hello from Exp 1!")""",
            """# Code Snippet 2\nprint("Hello from Exp 2!")""",
            """# Code Snippet 3\nprint("Hello from Exp 3!")""",
            """# Code Snippet 4\nprint("Hello from Exp 4!")""",
            """# Code Snippet 5\nprint("Hello from Exp 5!")""",
            """# Code Snippet 6\nprint("Hello from Exp 6!")""",
            """# Code Snippet 7\nprint("Hello from Exp 7!")""",
            """# Code Snippet 8\nprint("Hello from Exp 8!")""",
            """# Code Snippet 9\nprint("Hello from Exp 9!")""",
            """# Code Snippet 10\nprint("Hello from Exp 10!")""",
        ]

    def exp(self, index):
        if 1 <= index <= 10:
            print(self.codes[index - 1])
        else:
            print("Invalid experiment number. Choose between 1 and 10.")

# Create an instance for direct use
exp_runner = Experiments()
