import logging
import tkinter as tk  # https://tkdocs.com/
import speech_recognition as sr

# Set logging preferences
logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w',
                    format='%(module)s - %(levelname)s - %(message)s')


class App():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PARSE-EL-TONGUE")
        self.root.geometry('1100x750')
        self.root.configure(background='#707070')

        self.languages = {"Python": ".py", "JavaScript": ".js"}
        self.language = "Python"
        self.indent, self.structure, self.variables = 0, 1, []
        self.last = ""

        # Save field
        self.save_entry = tk.Entry(self.root, width=100, bg='#606060', fg='white')
        self.save_entry.grid(row=0, column=0, columnspan=2, padx=15, pady=15)
        self.save_entry.insert(0, "new_document.py")
        btn_save = tk.Button(self.root, text="Save File", command=lambda: self.save_file())
        btn_save.grid(row=0, column=2, padx=5, pady=5)

        # Main text entry
        self.code_entry = tk.Text(self.root, width=150, height=40, bg='#606060', fg='white')
        self.code_entry.grid(row=1, column=0, columnspan=3, padx=15, pady=15)

        # Speech-to-Text
        btn_speak = tk.Button(self.root, text="Speak", command=lambda: self.save_file())
        btn_speak.grid(row=2, column=1, padx=15, pady=15, columnspan=3, sticky="W")

        # Manual text entry
        self.NL_entry = tk.Entry(self.root, width=100, bg='#606060', fg='white')
        self.NL_entry.grid(row=3, column=0, columnspan=2, padx=15, pady=15)
        btn_NL = tk.Button(self.root, text="Interpret", command=lambda: self.write(self.NL_entry.get()))
        btn_NL.grid(row=3, column=2, padx=5, pady=5)

        self.root.mainloop()  # Draw window

    def save_file(self):
        with open(self.save_entry.get(), 'w') as file:
            file.write(self.code_entry.get('1.0', 'end'))

    def speech(self):
        pass
        # r = sr.Recognizer()
        # mic = sr.Microphone()
        # with mic as source:
        #     r.adjust_for_ambient_noise(source)
        #     audio = r.listen(source)
        # r.recognize_google(audio)

    def write(self, utterance):

        code = self.interpret(utterance, 'X')
        if code in ["No Matching Patterns Found!", "COMMAND"]:
            return

        code = code.replace("\\n ", "\n")
        code = code.replace("\\n", "\n")
        code = code.split("\n")
        for i in range(len(code)):
            code[i] = "\t" * self.indent + code[i]
            if "\\t " in code[i] or "\\t" in code[i]:
                code[i] = code[i].replace("\\t ", "\t")
                code[i] = code[i].replace("\\t", "\t")
                self.indent += 1
            if "\\b " in code[i] or "\\b" in code[i]:
                code[i] = code[i].replace("\t ", "", 1)
                code[i] = code[i].replace("\t", "", 1)
                code[i] = code[i].replace("\\b", "", 1)
                self.indent -= 1
        code = "\n".join(code)

        # Label things to be replaced
        for i in range(1, self.structure + code.count("<?>")):
            self.structure += 1
            code = code.replace("<?>", "<" + str(i) + ">", 1)

        code = self.code_entry.get("1.0", "end") + code
        self.code_entry.delete("1.0", "end")
        self.NL_entry.delete(0, "end")
        self.code_entry.insert("1.0", code)

    def command(self, command):
        print("COMMAND:", command)
        args = next(iter(command.values()))
        command = next(iter(command.keys()))
        code = self.code_entry.get("1.0", "end")

        if command in ["end block", "close block"]:
            self.indent -= 1
        if command == "undo":
            code = code.replace(self.last, "", 1)
        if command == "redo":
            code = code + self.last
        if command in ["replace X with X", "set X as x"]:
            code = code.replace("<" + args[0] + ">", self.interpret(args[1], 'X'), 1)
        if command == "comment X":
            code = code + ("\t" * self.indent) + "# " + args[0]
        if command == "new line":
            code = code + "\n"

        self.NL_entry.delete(0, "end")
        self.code_entry.delete("1.0", "end")
        self.code_entry.insert("1.0", code)


if __name__ == "__main__":
    Session = App()  # Create Window object
