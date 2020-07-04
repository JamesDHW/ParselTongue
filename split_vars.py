def split_vars(types, utt):

    def split(types, utt):
        solutions = []  # This is to be returned if we're not at max depth

        # At max depth check if the full utterance matches that type's interpretation
        if len(types) == 1 and all(types[0] in x for x in utt):
            return {types[0]: utt}  # Return dictionary (JSON)
        elif len(types) == 1:
            return False

        # Otherwise recurse for each variable
        for i in range(len(types)):
            for j in range(len(utt)):
                if all(types[i] in x for x in utt[:j+1]):
                    nex = split(types[i+1:], utt[j+1:])
                    if nex:
                        solutions.append({types[i]: utt[:j + 1]})
                        if type(nex) == list:
                            for sol in nex:
                                solutions.append(sol)
                        else:
                            solutions.append(nex)

        return solutions

    sols = split(types, utt)
    if len(sols) == 0:
        return False
    elif type(sols) == dict and len(next(iter(sols.values()))) > 0:
        return {next(iter(sols.keys())): " ".join(next(iter(sols.values())))}
    elif type(sols) == dict and len(next(iter(sols.values()))) > 0:
        return False

    # This is the order in which we should interpret
    # Should go from most to least specific
    prefs = ('B', 'A', 'D', 'C')

    match_template = {var: [] for var in types}
    matching = []
    for sol in sols:
        for x, y in match_template.items():
            if next(iter(sol)) == x:
                match_template[x] = " ".join(sol[next(iter(sol))])
        if types[-1] in sol.keys():
            matching.append(match_template.copy())

    for match in matching:
        print('Match found:', match)
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

    return matching[0]


if __name__ == "__main__":
    # sols is the returned value form the function
    print('\noptimum split:', split_vars(['A', 'B', 'C', 'D'], 'A A AB B B B BC C CD D'.split()))
    print("Vars: ['A', 'B', 'C', 'D'], NL statement: 'A A AB B B B BC C CD D'")
