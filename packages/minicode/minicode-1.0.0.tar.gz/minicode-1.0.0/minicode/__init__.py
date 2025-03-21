import re

def addcode(code, key, original_len):
    """
    解码函数，验证传入的 code 是否与 key 和 original_len 匹配。
    如果匹配，打印解码后的字符。
    """
    # 使用正则表达式提取数字部分
    match = re.search(r'\d+', code)
    if match:
        Tmp = match.group()  # 提取匹配到的数字
        print("Extracted number:", Tmp)  # 打印提取的数字部分，便于调试
        try:
            # 解码公式：提取的数字 - 输入字符串的长度
            TTemp = int(Tmp) - original_len
            if TTemp == key:
                Temp = chr(TTemp)
                print("Decoded character:", Temp)
            else:
                print("KEY ERROR! Expected key:", key, "but got:", TTemp)
        except ValueError:
            print("INVALID CODE!")
    else:
        print("NO NUMERIC PART FOUND IN CODE!")

def bancode(text):
    """
    编码函数，将输入的字符串中的每个字符进行编码。
    返回一个包含每个字符的编码结果（code, key, original_len）的列表。
    """
    result = []
    original_len = len(text)  # 输入字符串的长度
    for char in text:
        key = ord(char)  # 获取字符的 Unicode 编码值
        code = "--MINICODE--" + str(key + original_len)  # 生成加密代码
        result.append((code, key, original_len))  # 将 code、key、original_len 作为一个元组添加到结果列表中
    return result
