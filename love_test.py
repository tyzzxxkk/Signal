from utils import calculate_compatibility

def love_result_message(name1, name2):
    score = calculate_compatibility(name1, name2)
    if score >= 90:
        msg = "헐... 우리 혹시... 결혼까지....?"
    elif score >= 70:
        msg = "우리.... 연애 한 번 해볼까...?"
    elif score >= 50:
        msg = "우리 둘이 노력하면,,,, 뚜뚜루뚜뚜 가능!"
    else:
        msg = "띠로리"
    return score, msg
