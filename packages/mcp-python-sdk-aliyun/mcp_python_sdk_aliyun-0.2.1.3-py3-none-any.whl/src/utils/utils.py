import random
import string
import time


def generate_random_string(length=16):
    # 定义字符集：小写字母 + 数字
    characters = string.ascii_lowercase + string.digits

    # 从定义的字符集中随机选择字符并组合成指定长度的字符串
    random_str = ''.join(random.choice(characters) for _ in range(length))
    return random_str


def generate_custom_trace_id():
    return str(int(round(time.time() * 1000))) + generate_random_string(12)


if __name__ == '__main__':
    print(generate_random_string(8))
    print(generate_custom_trace_id())
