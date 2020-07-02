class interpreter:
    def __init__(self, lang):
        self.language = lang
        self.patterns, self.commands = self.load_patterns()  # Patterns
        self.no = 0

    def load_patterns(self):
        """
        Loads natural language statements and corresponding code snippets.
        Also loads some natural language commands in a list.
        :return: dict of dicts containing { NL_1 : code_snip_1, ... }, [ NL_command_1, ... ]
        """
        types = {'X': '/main.txt', 'B': '/bool.txt', 'V': '/main.txt'}
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
        print('interpretation', self.no)
        self.no += 1
        pattern = self.match_str(utterance, d_type)  # Find the most specific match with anything else to interpret

        # Atomic decisions
        if not pattern: # No matching patterns
            return False
            # # If the utterance is a known variable name
            # if "_".join(utterance.split(" ")) in ['self.variables']:
            #     print("var found")
            #     return "_".join(utterance.split(" "))
            # # Else return absolute value
            # val = "'" + utterance + "'"
            # try:
            #     if int(utterance) - float(utterance) == 0:
            #         val = int(utterance)
            #     else:
            #         val = float(utterance)
            # except:
            #     pass
            #
            # return str(val)

        code = list(pattern.keys())[0]  # string of code potentially has some patterns still in e.g. if B : \\n\\tX
        utt = list(pattern.values())[0]  # potential extra bits to interpret
        interps = [x for x in code.split() if x.isupper()]  # Extra vars to be interpreted

        iter = 0
        for element in interps:
            if element.isupper():
                print(pattern)
                code = code.replace(element, self.interpret(utt[iter], element), 1)
                iter += 1

        # self.last = code
        return code

    def match_str(self, utt, d_type='X'):
        """
        :param utterance: string of natural language to be matched to a pattern
        :param d_type: type of utterance (boolean statement/ string?)
        :return: dictionary of {interpreted code : list of variables}
        """
        print("#" * 50)
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
                            print("Ends in variable(s)")

                            # Now need to split multiple vars e.g. B X, "'A is True' 'print B'"
                            if len(remaining_upp) > 1:
                                split = self.split_vars(remaining_upp, utterance[i:])
                                if not split: break
                                for x, y in split.items():
                                    solution_vars.append(split[x])
                            else:
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
                        length = len(p)
                        while len(u) >= length:
                            # print(p[i], u[i])
                            if p[i].isupper():  # If next var is also upper
                                # Multi variable condition
                                while len(u) >= len(p):
                                    print('-'*10)
                                    print(p[i], u[i])
                                    # print('hey', caps)
                                    print('both', len(u), length)
                                    if p[i].isupper():
                                        caps.append(p.pop(i))
                                        print('hey', caps)
                                    if u[i] != p[i]:
                                        var.append(u.pop(i))
                                        print('hey', u[i], p[i])
                                        print('both2', len(u), length)
                                        pattern.pop(i +1)
                                        utterance.pop(i + 1)  # Also remove extra length from utterance
                                    else:
                                        print('heyooo', caps, var)
                                        split = self.split_vars(caps, var)
                                        print('split =', split)
                                        if not split:
                                            no_match = True
                                            var.append(u.pop(i))
                                            continue    # Allows repeated phrases
                                        for x, y in split.items():
                                            solution_vars.append(split[x])
                                        break   # Break if split worked
                            elif u[i] != p[i]:
                                var.append(u.pop(i))
                                pattern.pop(i + 1)
                                utterance.pop(i + 1)  # Also remove extra length from utterance
                            else:
                                # Found a match
                                # "X" pattern, solution found
                                print("found var for ", pattern[i], "-", " ".join(var))
                                solution_vars.append(" ".join(var))
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
            print("solutions", solutions)

            # Sort solutions and select the first key and value
            solutions = {k: solutions[k] for k in sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key))}
            code = next(iter(solutions.keys()))
            vars = next(iter(solutions.values()))

            print("solution:", {code: vars})
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
            print('splitting', types, utt)
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
                    print('interpreting,', utt[:j + 1], types[i])
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
                        print('failed')

            return solutions  # Returns a list of dictionaries from deeper depths

        sols = split(types, utt)
        print('sols:', sols)
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

        print('matching[0]: ', matching[0])
        return matching[0]


interpreter = interpreter('Python')
print('final matching code:', interpreter.interpret('if a b c then'))
