def calculate_name_score(name):
    score = sum([ord(char) for char in name])
    return score

def calculate_compatibility(name1, name2):
    score1 = calculate_name_score(name1)
    score2 = calculate_name_score(name2)
    result = (score1 + score2) % 101
    return result
