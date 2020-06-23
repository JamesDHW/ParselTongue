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
        self.patterns, self.commands = self.load_patterns()  # Patterns
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

    def load_patterns(self):
        # Load Patterns
        with open(self.language + "/main.txt") as file:
            raw = list(file)

        patterns, commands = {}, []
        for i in range(len(raw)):
            if "#" not in raw[i]:
                ls = raw[i].split(" :: ")
                if len(ls) == 2:
                    patterns[ls[0]] = ls[1].strip("\n")
                    if ls[1].strip("\n") == 'command':
                        commands.append(ls[0])
        return patterns, commands

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

        code = self.interpret(utterance)
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
            code = code.replace("<?>", "<"+str(i)+">", 1)

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
            code = code.replace("<"+args[0]+">", self.interpret(args[1]), 1)
        if command == "comment X":
            code = code + ("\t"*self.indent) + "# " + args[0]
        if command == "new line":
            code = code + "\n"

        self.NL_entry.delete(0, "end")
        self.code_entry.delete("1.0", "end")
        self.code_entry.insert("1.0", code)

    def interpret(self, utterance):

        pattern = self.match_str(utterance)

        # Atomic decisions
        if pattern == "No Matching Patterns Found!":

            # If the utterance is a known variable name
            if "_".join(utterance.split(" ")) in self.variables:
                print("var found")
                return "_".join(utterance.split(" "))
            # Else return absolute value
            val = "'" + utterance + "'"
            try:
                if int(utterance) - float(utterance) == 0:
                    val = int(utterance)
                else:
                    val = float(utterance)
            except:
                pass

            return str(val)

        code = list(pattern.keys())[0]
        iter = 0
        for element in code:
            if element.isupper():
                code = code.replace(element, self.interpret(pattern[list(pattern.keys())[0]][iter]), 1)
                iter += 1
        self.last = code
        return code

    def match_str(self, utt):
        print("#"*25)
        solutions = {}  # Dict of all possible matches
        # For each pattern
        for x, y in self.patterns.items():
            # Key of dict must match utterance
            # Value of key is corresponding code
            pattern = x.split(" ")
            utterance = utt.split(" ")
            # Quickly remove any impossible matches
            if any(x in pattern for x in utterance) and len(utterance) >= len(pattern):
                solution = []
                # Loop through every literal in the pattern
                for i in range(len(pattern)):

                    # If matching then solution found
                    # print(pattern[i:], utterance[i:])
                    if pattern[i:] == utterance[i:]:
                        if y == "command":
                            solutions[x] = solution
                        else:
                            solutions[y] = solution
                        print('solution found:', y)
                        break

                    if utterance[i] == pattern[i]:
                        # Matching so far
                        # print("Matching word:", pattern[i])
                        continue
                    elif pattern[i].isupper():
                        # If pattern ends in variable
                        if i + 1 == len(pattern):
                            print("Ends in variable")
                            # "X" or "N" pattern, solution found
                            if pattern[i] in ["X", "N"]:
                                solution.append(" ".join(utterance[i:]))
                            # "V" pattern solution found if known variable
                            elif pattern[i] == "V":
                                if "_".join(utterance[i:]) not in self.variables:
                                    break
                                solution.append("_".join(utterance[i:]))
                            # Add solution to solutions
                            if y == "command":
                                solutions[x] = solution
                            else:
                                solutions[y] = solution
                            print('solution found:', y)
                            break

                        # Now looking for next occurrence of pattern literal
                        # As there must be another literal after X
                        p, u = pattern.copy(), utterance.copy()
                        utterance[i] = pattern[i]  # For neatness sake
                        del p[i]  # Delete 'X', reduce list size
                        var = [u.pop(i)]  # Add to this until next literal found
                        no_match = False
                        while len(u) >= len(p):
                            if u[i] != p[i]:
                                # For each incorrect we also check if a known variable is present
                                print(pattern[i], "_".join(var), self.variables)
                                if pattern[i] == "V" and "_".join(var) in self.variables:
                                    # Check if next word is also part of variable
                                    if len(u) > len(p) and "_".join(var) + "_" + u[i] in self.variables:
                                        var.append(u.pop(i))
                                        utterance.pop(i + 1)  # Also remove extra length from utterance
                                        continue
                                    solution.append("_".join(var))
                                    break
                                else:
                                    var.append(u.pop(i))
                                    utterance.pop(i + 1)  # Also remove extra length from utterance
                            else:
                                # Found a match
                                # "X" pattern, solution found
                                print("found var for ", pattern[i], "-", "_".join(var))
                                if pattern[i] == "X":
                                    solution.append(" ".join(var))
                                # "N" pattern, add to variables, solution found
                                elif pattern[i] == "N":
                                    solution.append("_".join(var))
                                    try:
                                        float("_".join(var))
                                        int("_".join(var)[0])
                                        no_match = True  # No solution
                                    except:
                                        if "-" in "_".join(var):
                                            no_match = True  # No solution

                                break
                            # Loop about to be broken with no match found
                            if len(u) < len(p):
                                no_match = True  # No solution
                        print(solution, pattern[i])
                        if no_match:
                            print("No match", pattern, utterance)
                            # print(pattern[i:], utterance[i:])
                            break

                    else:
                        # No match, don't add solution, move on
                        break

        # Select most specific pattern
        if len(solutions) != 0:
            # print("sorted keys", sorted_keys)
            # print("sorted", sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key)))
            # print("solutions", solutions)

            # Sort solutions and select the first key and value
            solutions = {k: solutions[k] for k in sorted(solutions, key=lambda key:  len(" ".join(solutions[key])) / len(key))}
            code = next(iter(solutions.keys()))
            vars = next(iter(solutions.values()))

            # If key is command, execute command
            print(self.commands)
            if code in self.commands:
                self.command({code: vars})
                return

            j = 0
            for i in [a for a in code if a.isupper()]:
                if i == "X": j += 1
                else:
                    if i == "N":
                        self.variables.append(vars[j])
                    code = code.replace(i, vars.pop(j), 1)

            print("solution:", {code: vars})
            return {code: vars}
        else:
            return "No Matching Patterns Found!"


if __name__ == "__main__":
    Session = App()  # Create Window object
