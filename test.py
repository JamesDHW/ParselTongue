# Match an utterance to a pattern
def match_str(self, utterance):
    utterance = utterance.split(" ")

    solutions = {}
    for element in self.patterns:
        pattern = list(element.keys())[0].split(" ")
        # quickly checks for non-matching patterns which share no similar words
        if any(x in pattern for x in utterance) and len(utterance) >= len(pattern):
            # print("ele", element)
            # for a given pattern
            solution = []
            iter = 0
            for i in range(len(pattern)):
                # If pattern matches exactly, continue
                if pattern[i] == utterance[iter]:
                    # If pattern ends in literal
                    if i + 1 == len(pattern) and iter + 1 == len(utterance):
                        if element[" ".join(pattern)] == 'command':
                            self.command({" ".join(pattern): solution})
                            return "COMMAND"
                        else:
                            solutions[element[" ".join(pattern)]] = solution
                        break
                    iter += 1
                    continue
                # pattern[i] is a variable
                elif pattern[i].isupper():
                    var = [str(utterance[iter])]
                    iter += 1
                    # If end of the pattern not reached
                    if i + 1 < len(pattern):
                        # Add the utterance word as a variable
                        # until another pattern word is found
                        while iter + 1 < len(utterance):
                            # Check if known variable
                            if pattern[i] == "V":
                                if ("_".join(utterance[i:iter]) in self.variables) and (
                                        "_".join(utterance[i:iter + 1]) not in self.variables):
                                    print("_".join(utterance[i:iter]), "_".join(utterance[i:iter + 1]))
                                    print(self.variables)
                                    # This will override the whole pattern!!!
                                    element[" ".join(pattern)] = element[" ".join(pattern)].replace("V", "_".join(
                                        utterance[i:iter]), 1)
                                    break
                                else:
                                    iter += 1
                                    continue
                            elif pattern[i + 1] == utterance[iter]:
                                solution.append(" ".join(var))
                                break
                            else:
                                var.append(utterance[iter])
                            iter += 1
                    else:
                        # Reached the end of the pattern
                        # Add the rest of the utterance as a variables
                        while iter < len(utterance):
                            var.append(utterance[iter])
                            iter += 1
                        solution.append(" ".join(var))
                        if " ".join(pattern) in element.keys() and element[" ".join(pattern)] == 'command':
                            self.command({" ".join(pattern): solution})
                            return "COMMAND"
                        else:
                            # print(type(element[" ".join(pattern)]))
                            # print(element[" ".join(pattern)])
                            # print(type(" ".join(pattern)))
                            solutions[element[" ".join(pattern)]] = solution
                        break

                    continue
                # Not matching and pattern[i] not a variable
                else:
                    # print("NOT MATCH")
                    break

    # Select most specific pattern
    if len(solutions) != 0:

        sorted_keys = sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key))
        print("solutions", solutions)
        print("sorted keys", sorted_keys)

        print("solution:", {sorted_keys[0]: solutions[sorted_keys[0]]})
        return {sorted_keys[0]: solutions[sorted_keys[0]]}
    else:
        return "No Matching Patterns Found!"


# for word in pattern:
#     if word == utterance[i]:
#         good move on
#     elif type V:
#     elif type N:
#     elif type I:
#     else:
#         no match


known_vars = ["a", "a_a", "for_b"]
# patterns = {"for N in V X": "for N in V : \\n \\t X"}
patterns = {"for V in X": "for X in : \\n \\t print(a)", "X in V": "blah blah blah"}


# itter = iter(known_vars)
# print(next(itter))
# print(known_vars.pop(1))
# print(known_vars)


def new_match_string(utt):
    solutions = {}  # Dict of all possible matches
    # For each pattern
    for x, y in patterns.items():
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
                    solutions[x] = solution
                    solutions[y] = solution
                    break

                if utterance[i] == pattern[i]:
                    # Matching so far
                    # print("Matching word")
                    continue
                elif pattern[i].isupper():
                    # If pattern ends in variable
                    if i + 1 == len(pattern):
                        print("Ends in variable")
                        # "X" pattern, solution found
                        if pattern[i] == "X":
                            solution.append(" ".join(utterance[i:]))
                        # "N" pattern, add to variables, solution found
                        elif pattern[i] == "N":
                            solution.append("_".join(utterance[i:]))
                            known_vars.append("_".join(utterance[i:]))
                        # "V" pattern solution found if known variable
                        elif pattern[i] == "V":
                            solution.append("_".join(utterance[i:]))
                            if "_".join(utterance[i:]) not in known_vars:
                                break
                        # Add solution to solutions
                        solutions[x] = solution
                        solutions[y] = solution
                        break

                    # Now looking for next occurrence of pattern literal
                    # As there must be another literal after X
                    p, u = pattern.copy(), utterance.copy()
                    utterance[i] = pattern[i]  # For neatness sake
                    del p[i]  # Delete 'X', reduce list size
                    var = [u.pop(i)]  # Add to this until next literal found
                    no_match = False
                    while len(u) >= len(p):
                        print(u, p)
                        print("looping", len(p), len(u), var)
                        if u[i] != p[i]:
                            # print(u[i], "!=", p[i])
                            # For each incorrect we also check if a known variable is present
                            if pattern[i] == "V" and "_".join(var) in known_vars:
                                # Check if next word is also part of variable
                                if len(u) > len(p) and "_".join(var) + "_" + u[i] in known_vars:
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
                            if pattern[i] == "X":
                                solution.append(" ".join(var))
                            # "N" pattern, add to variables, solution found
                            elif pattern[i] == "N":
                                solution.append("_".join(var))
                                try:
                                    float("_".join(var))
                                    int("_".join(var)[0])
                                    no_match = True  # No solution
                                    print("S")
                                except:
                                    print("F")
                                    known_vars.append("_".join(var))
                            # "V" pattern solution found if known variable
                            elif pattern[i] == "V":
                                solution.append("_".join(var))
                                # print("var", "_".join(var))
                                if "_".join(var) not in known_vars:
                                    no_match = True  # No solution
                            break
                        # Loop about to be broken with no match found
                        if len(u) < len(p):
                            # print(" len(u) == len(p)")
                            no_match = True  # No solution
                    if no_match:
                        print("No match", pattern, utterance)
                        # print(pattern[i:], utterance[i:])
                        break

                else:
                    # No match, don't add solution, move on
                    # print("Don't match", pattern[i], utterance[i])
                    break

    # Substitute N and V as literals
    for x, y in solutions.copy().items():

        j = 0
        for i in [a for a in x if a.isupper()]:
            # Don't sub variables for X
            if i == "X":
                j += 1
            else:
                del solutions[x]
                x = x.replace(i, y.pop(j), 1)
                solutions[x] = y

    # If key is command, execute command
    if x == "COMMAND":
        pass

    # Select most specific pattern
    if len(solutions) != 0:

        sorted_keys = sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key))
        print("solutions", solutions)
        print("sorted keys", sorted_keys)

        print("solution:", {sorted_keys[0]: solutions[sorted_keys[0]]})
        return {sorted_keys[0]: solutions[sorted_keys[0]]}
    else:
        return "No Matching Patterns Found!"


print(new_match_string("1 in for b"))


# Match an utterance to a pattern
def match_str(self, utterance):
    utterance = utterance.split(" ")

    solutions = {}
    for element in self.patterns:
        pattern = list(element.keys())[0].split(" ")
        # quickly checks for non-matching patterns which share no similar words
        if any(x in pattern for x in utterance) and len(utterance) >= len(pattern):
            # print("ele", element)
            # for a given pattern
            solution = []
            iter = 0
            for i in range(len(pattern)):
                # If pattern matches exactly, continue
                if pattern[i] == utterance[iter]:
                    # If pattern ends in literal
                    if i + 1 == len(pattern) and iter + 1 == len(utterance):
                        if element[" ".join(pattern)] == 'command':
                            self.command({" ".join(pattern): solution})
                            return "COMMAND"
                        else:
                            solutions[element[" ".join(pattern)]] = solution
                        break
                    iter += 1
                    continue
                # pattern[i] is a variable
                elif pattern[i] in ["X", "N"]:
                    var = [str(utterance[iter])]
                    iter += 1
                    # If end of the pattern not reached
                    if i + 1 < len(pattern):
                        # Add the utterance word as a variable
                        # until another pattern word is found
                        while iter + 1 < len(utterance):
                            if pattern[i + 1] == utterance[iter]:
                                solution.append(" ".join(var))
                                break
                            else:
                                var.append(utterance[iter])
                            iter += 1
                    else:
                        # Reached the end of the pattern
                        # Add the rest of the utterance is a variables
                        while iter < len(utterance):
                            var.append(utterance[iter])
                            iter += 1
                        solution.append(" ".join(var))
                        if " ".join(pattern) in element.keys() and element[" ".join(pattern)] == 'command':
                            self.command({" ".join(pattern): solution})
                            return "COMMAND"
                        else:
                            # print(type(element[" ".join(pattern)]))
                            # print(element[" ".join(pattern)])
                            # print(type(" ".join(pattern)))
                            solutions[element[" ".join(pattern)]] = solution
                        break

                    continue
                elif pattern[i] == "V":
                    while iter + 1 < len(utterance):
                        if ("_".join(utterance[i:iter]) in self.variables) and (
                                "_".join(utterance[i:iter + 1]) not in self.variables):
                            print("_".join(utterance[i:iter]), "_".join(utterance[i:iter + 1]))
                            print(self.variables)
                            # This will override the whole pattern!!!
                            element[" ".join(pattern)] = element[" ".join(pattern)].replace("V", "_".join(
                                utterance[i:iter]), 1)
                            break
                        else:
                            iter += 1
                            continue
                        if pattern[i + 1] == utterance[iter]:
                            solution.append(" ".join(var))
                            break
                        else:
                            var.append(utterance[iter])
                        iter += 1
                # Not matching and pattern[i] not a variable
                else:
                    # print("NOT MATCH")
                    break

    # Select most specific pattern
    if len(solutions) != 0:

        sorted_keys = sorted(solutions, key=lambda key: len(" ".join(solutions[key])) / len(key))
        print("solutions", solutions)
        print("sorted keys", sorted_keys)

        print("solution:", {sorted_keys[0]: solutions[sorted_keys[0]]})
        return {sorted_keys[0]: solutions[sorted_keys[0]]}
    else:
        return "No Matching Patterns Found!"
