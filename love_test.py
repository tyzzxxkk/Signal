from utils import calculate_compatibility

def love_result_message(name1, name2):
    score = calculate_compatibility(name1, name2)
    if score >= 90:
        msg = "운명의 상대! 완벽한 궁합!"
    elif score >= 70:
        msg = "꽤 잘 맞는 편이에요!"
    elif score >= 50:
        msg = "노력하면 잘 될 사이!"
    else:
        msg = "친구로 지내기에 딱 좋아요!"
    return score, msg
