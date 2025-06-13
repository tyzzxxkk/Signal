from utils import calculate_compatibility

def love_result_message(name1, name2):
    score = calculate_compatibility(name1, name2)
    if score >= 90:
        msg = "헐... 그냥 운명 그 자체잖아 💕✨"
    elif score >= 60:
        msg = "우리.. 썸 한 번 타볼까? 낫배드!"
    elif score >= 30:
        msg = "우리 잘되려면... 서로 노력 많이 해보자 ㅎㅎ"
    else:
        msg = "띠로리.. 우리 착각이었나봐.. 💔"
    return score, msg
