class interpreter:
    """
    X - Default/ base interpretation library.
    B - Boolean statement.
    N - Variable name (new or existing).
    V - Value consisting of primitive types and variable names.
    """
    def __init__(self, lang):
        self.language = lang
        self.patterns, self.commands = self.load_patterns()  # Patterns
        self.variables = []

        with open(self.language + '/values_default.txt', 'r') as template:
            lines = list(template.read())
            with open(self.language + '/values.txt', 'w') as file:
                for line in lines:
                    file.write(line)

    def load_patterns(self):
        """
        Loads natural language statements and corresponding code snippets.
        Also loads some natural language commands in a list.
        :return: dict of dicts containing { NL_1 : code_snip_1, ... }, [ NL_command_1, ... ]
        """
        types = {'X': '/main.txt', 'B': '/bool.txt', 'V': '/values.txt'}
        patterns = {'X': {}, 'B': {}, 'V': {}}
        commands = []

        # Load patterns
        for x, y in types.items():
            with open(self.language + y) as file:
                for line in list(file):
                    if "#" not in line:
                        ls = line.split(" :: ")
                        if len(ls) == 2:
                            patterns[x][ls[0]] = ls[1].strip("\n")
                            if ls[1].strip("\n") == 'command':
                                commands.append(ls[0])

        return patterns, commands

    def interpret(self, utterance, d_type='X'):
        """
        Recursive function to return desired code from NL.
        :param utterance: Natural Language string.
        :param d_type: Repertoire file used for interpretation of utterance.
        :return: code string corresponding to utterance.
        """
        def interp_value(value):
            # Could be a combination of known variables, strings, ints, floats
            if value in self.variables: return value
            nex = self.interpret(value, 'V')
            if not nex:
                try:
                    if int(value) - float(value) == 0:
                        return str(int(value))
                    else:
                        return str(float(value))
                except:
                    return "'" + value + "'"
            else:
                return nex

        if d_type == "N":
            return '_'.join(utterance.split())

        print('interpreting "%s", d_type: %s' % (utterance, d_type))
        pattern = self.match_str(utterance, d_type)  # Find the most specific match with anything else to interpret

        # No matching patterns
        if not pattern:
            return False

        code = list(pattern.keys())[0]  # string of code potentially has some patterns still in e.g. if B : \\n\\tX
        utt = list(pattern.values())[0]  # potential extra bits to interpret
        interps = [x for x in code if x.isupper()]  # Extra vars to be interpreted

        # Reinterpret other variables
        for i in range(len(interps)):
            # New variable name always returns of format 'var_name', also saves new names
            if interps[i] == 'N':
                self.variables.append('_'.join(utt[i].split()))
                code = code.replace('N', '_'.join(utt[i].split()), 1)
            # String literal
            elif interps[i] == 'S':
                code = code.replace('S', "'"+utt[i]+"'", 1)
            # Value
            elif interps[i] == 'V':
                code = code.replace('V', interp_value(utt[i]), 1)
            else:
                nex = self.interpret(utt[i], interps[i])
                if nex:
                    code = code.replace(interps[i], nex, 1)
                else:
                    return False
        return code

    def match_str(self, utt, d_type='X'):
        """
        :param utt: string of natural language to be matched to a pattern
        :param d_type: type of utterance (boolean statement/ string?)
        :return: dictionary of {interpreted code : list of variables}
        """
        print("#" * 25, "Matching String:", utt, "#" * 25)
        solutions = {}  # Dict of all possible matches to choose a return value from
        # For each pattern
        for patt, code in self.patterns[d_type].items():
            # Key of dict must match utterance
            # Value of key is corresponding code
            pattern = patt.split(" ")
            utterance = utt.split(" ")
            # Quickly remove any impossible matches
            if any(x in pattern for x in utterance) and len(utterance) >= len(pattern):
                solution_vars = []
                print("PATTERN:", pattern)
                # Loop through every literal in the pattern
                for i in range(len(pattern)):
                    print('break:', i, utterance, pattern)

                    # If matching then solution found
                    print(pattern[i:], utterance[i:])
                    if pattern[i:] == utterance[i:]:
                        if code == "command":
                            solutions[patt] = solution_vars
                        else:
                            solutions[code] = solution_vars
                        print('solution found:', code)
                        break
                    elif utterance[i] == pattern[i]:
                        # Matching so far
                        continue
                    elif pattern[i].isupper():
                        # If pattern ends in variable (i + no. of remaining upper-cases)
                        remaining_upp = [x for x in pattern[i:] if x.isupper()]
                        if i + len(remaining_upp) == len(pattern):
                            print("Ends in variable(s)", remaining_upp, utterance[i:], solution_vars)

                            # Now need to split multiple vars e.g. B X, "'A is True' 'print B'"
                            if len(remaining_upp) > 1:
                                print("SPLITTING")
                                split = self.split_vars(remaining_upp.copy(), utterance[i:].copy())
                                if not split: break
                                for x, y in split.items():
                                    print('appending end split:', split[x])
                                    solution_vars.append(split[x])
                            else:
                                print('appending end join:', " ".join(utterance[i:]))
                                solution_vars.append(" ".join(utterance[i:]))

                            # Add solution to solutions
                            if code == "command":
                                solutions[patt] = solution_vars
                            else:
                                solutions[code] = solution_vars
                            print('solution found:', code)
                            break

                        # Now looking for next occurrence of pattern literal
                        # as there must be another literal after X
                        p, u = pattern.copy(), utterance.copy()
                        caps = [p.pop(i)]  # Delete 'X', reduce list size
                        var = [u.pop(i)]  # Add to this until next literal found
                        no_match = False
                        single = True
                        length = len(p)
                        while len(u) >= length:
                            print('p, u', p[i], u[i])
                            if p[i].isupper():  # If next var is also upper
                                single = False  # Avoids repeating previous utterance words
                                print('UPPER')
                                # Multi variable condition
                                while len(u) >= len(p):
                                    if p[i].isupper():
                                        caps.append(p.pop(i))
                                    if u[i] != p[i]:
                                        print('not equal', u[i])
                                        var.append(u.pop(i))
                                        pattern.pop(i)
                                        utterance.pop(i)  # Also remove extra length from utterance
                                    else:
                                        print('heyooo', caps, var)
                                        split = self.split_vars(caps.copy(), var.copy())
                                        print('split =', split)
                                        if not split:
                                            no_match = True
                                            var.append(u.pop(i))
                                            continue    # Allows repeated phrases
                                        for x, y in split.items():
                                            print('appending', split[x])
                                            solution_vars.append(split[x])
                                        del utterance[i]
                                        print('remaining u,p', u, p, 'utt, patt', utterance, pattern)
                                        break   # Break if split worked
                            elif u[i] != p[i]:
                                var.append(u.pop(i))
                                utterance.pop(i + 1)  # Also remove extra length from utterance
                            else:
                                # Found a match
                                solution_vars.append(" ".join(var))
                                break

                            if not single:
                                break
                            # Loop about to be broken with no match found
                            if len(u) < len(p):
                                no_match = True  # No solution
                        # print(solution_vars, pattern[i])
                        if no_match:
                            print("No match", pattern, utterance)
                            # print(pattern[i:], utterance[i:])
                            break

                    else:
                        # No match, don't add solution, move on
                        print("No match", pattern, utterance)
                        break

        # Select most specific pattern
        if len(solutions) == 0:
            return False
        else:
            # print("sorted", sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key)))
            # print("solutions", solutions)

            # Sort solutions and select the first key and value
            solutions = {k: solutions[k] for k in sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key))}
            code = next(iter(solutions.keys()))
            vars = next(iter(solutions.values()))

            print("match_str solution:", {code: vars})
            return {code: vars}

    def split_vars(self, types, utt):
        # TODO: update evaluation to interpret
        """
        If a pattern contains two adjacent statements, split_vars determines which part
        of the utterance is associated with which statements/ interpretations.
        :return: { 'A' : 'A B', ... }
        """
        def split(types, utt):
            """
            Recursive function to return all possible valid splits.
            :param types: list of interpretations e.g. ['B', 'X']
            :param utt: list of words to be split up.
            :return: e.g. [ { 'B' : ['', ... , ''] }, { 'X'  : ['', ... , ''] }, ... ]
            """
            print('### splitting', utt, 'into', types, '###')
            solutions = []  # This is to be returned if we're not at max depth

            # At max depth check if the full utterance matches that type's interpretation
            if len(types) == 1 and self.interpret(" ".join(utt), types[0]):
                return {types[0]: utt}  # Return dictionary (JSON)
            elif len(types) == 1:
                return False

            # Otherwise recurse for each variable
            for i in range(len(types)):
                # For each word in the utterance
                for j in range(len(utt)):
                    # If the type is in the ('A') is in every word increasing forwards (e.g. 'A','A','AB')
                    # print('interpreting,', utt[:j + 1], types[i])
                    if self.interpret(" ".join(utt[:j + 1]), types[i]):
                        print('nex()', types[i + 1:], utt[j + 1:])
                        nex = split(types[i + 1:], utt[j + 1:])  # Work out next depth
                        print('nex:', nex)
                        if nex:  # If next depth is not False (is some valid answer)
                            solutions.append({types[i]: utt[:j + 1]})  # Add current
                            if type(nex) == list:  # Not at max depth returns a list of dictionaries/ JSON
                                for sol in nex:
                                    solutions.append(sol)
                            else:  # At max depth it just returns a dictionary
                                solutions.append(nex)
                    else:
                        print('failed split interpretation')

            return solutions  # Returns a list of dictionaries from deeper depths

        sols = split(types, utt)
        # print('sols:', sols)
        if len(sols) == 0:
            return False
        elif type(sols) == dict and len(next(iter(sols.values()))) > 0:
            return {next(iter(sols.keys())): " ".join(next(iter(sols.values())))}
        elif type(sols) == dict and len(next(iter(sols.values()))) > 0:
            return False

        # This is the order in which we should interpret
        # Should go from most to least specific
        prefs = ('B', 'X', 'D', 'C')

        match_template = {var: [] for var in types}
        matching = []
        for sol in sols:
            for x, y in match_template.items():
                if next(iter(sol)) == x:
                    match_template[x] = " ".join(sol[next(iter(sol))])
            if types[-1] in sol.keys():
                matching.append(match_template.copy())

        i = 0
        while len(matching) > i:
            for val in matching[i].values():
                if len(val) == 0:
                    del matching[i]
                    i -= 1
                    break
            i += 1

            if len(matching) == 0:
                return False

        for pref in prefs:
            i = 0
            while len(matching) > i + 1:
                if len(matching[i][pref]) < len(matching[i + 1][pref]):
                    del matching[:i + 1]
                    i = 0
                elif len(matching[i][pref]) == len(matching[i + 1][pref]):
                    i += 1
                else:
                    del matching[i + 1]
                    i = 0

        print('FINAL SPLIT:', matching[0])
        return matching[0]


if __name__ == "__main__":

    interpreter = interpreter('Python')
    while True:
        utterance = input("Natural Language to Interpret: ")
        if utterance == "": break
        code = interpreter.interpret(utterance)
        if not code: code = "No Match Found!"
        print('final matching code:\n' + code)

    print('\nInterpretation Ended')
