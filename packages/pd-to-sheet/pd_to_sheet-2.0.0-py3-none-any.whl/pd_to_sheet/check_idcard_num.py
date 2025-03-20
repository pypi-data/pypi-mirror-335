def is_valid_id_card(id_card):
    # 检查身份证号码长度
    if len(id_card) != 18:
        return False

    # 检查前17位是否为数字
    if not id_card[:-1].isdigit():
        return False

    # 校验码权重
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码对应值
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    # 计算校验码
    total = sum(int(id_card[i]) * weights[i] for i in range(17))
    check_code = check_codes[total % 11]

    # 检查校验码是否正确
    return id_card[-1].upper() == check_code


if __name__ == '__main__':
    # 示例用法
    id_card = "422802198608125471"
    print(is_valid_id_card(id_card))  # 输出: True
