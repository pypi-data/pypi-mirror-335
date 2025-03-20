import math


# 获取一个整数的某位的值
def digit_pos(num, pos):
    _max = math.floor(math.log(num, 10))  # 最大是几位数
    if pos > _max:
        raise Exception('{} 的最大位数是 {} 但是传入的是 {}'.format(num, _max, pos))
    # 移位操作: num // 10**pos 相当于将数字向右移动pos位，丢弃右边的数字
    # 提取操作: % 10 提取结果的个位数字
    return num // 10 ** pos % 10


if '__main__' == __name__:
    print(digit_pos(199, 1))
