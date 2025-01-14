import ddddocr
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import re


def clean_ocr_result(result):
    """
    清理 OCR 识别结果，修正常见误识别字符，并确保只有一个运算符。
    """
    result = result.replace('？', '=').replace('＝', '=').replace(' ', '')  # 替换误识别的符号
    allowed_chars = '0123456789+-*x='
    result = ''.join([char for char in result if char in allowed_chars])  # 过滤无效字符

    # 确保只有一个运算符和一个等号
    operators = re.findall(r'[+\-*x]', result)
    if len(operators) != 1:
        print(f"调试信息: 表达式中发现多个运算符或无效格式: {result}")
        return result  # 返回以供用户检查

    return result


def validate_expression(expression):
    """
    验证数学表达式格式是否正确。
    """
    pattern = r"^\d+[\+\-\*x]\d+=?$"  # 匹配类似 "1+2=" 的表达式
    return re.match(pattern, expression) is not None


def calculate_expression(expression):
    """
    计算简单数学表达式的结果。
    """
    try:
        expression = expression.rstrip("=")  # 去掉尾部的 "="
        for operator in ['+', '-', '*', 'x']:
            if operator in expression:
                operands = expression.split(operator)
                if len(operands) == 2:
                    num1, num2 = int(operands[0].strip()), int(operands[1].strip())
                    if operator in ['x', '*']:
                        return num1 * num2
                    elif operator == '+':
                        return num1 + num2
                    elif operator == '-':
                        return num1 - num2
    except ValueError as e:
        print(f"错误: 无法解析表达式 {expression}，错误信息: {e}")
    return None


def process_image(image_path):
    """
    处理验证码图片：OCR识别、清理、校验和计算。
    :param image_path: 验证码图片路径
    """
    ocr = ddddocr.DdddOcr(show_ad=False)

    try:
        # 读取图片数据
        with open(image_path, 'rb') as f:
            image_data = f.read()
        print(f"成功加载图片: {image_path}")
    except Exception as e:
        print(f"错误: 无法加载图片 {image_path}，错误信息: {e}")
        return

    # OCR 识别
    ocr_result = ocr.classification(image_data).strip()[:3]  # 限制结果为前三个字符，看需要可以限制多位数
    print(f"OCR 识别结果（截取前三个字符）: {ocr_result}")

    # 清理 OCR 结果
    ocr_result = clean_ocr_result(ocr_result)
    print(f"清理后的 OCR 结果: {ocr_result}")

    # 验证并计算结果
    if validate_expression(ocr_result):
        calculation_result = calculate_expression(ocr_result)
        if calculation_result is not None:
            print(f"识别内容: {ocr_result}，计算结果: {calculation_result}")
            return calculation_result
    else:
        print("OCR 结果无效，请手动输入正确表达式。")
        while True:
            manual_input = input("请输入正确的表达式（例如: 1*6=）：").strip()
            if validate_expression(manual_input):
                calculation_result = calculate_expression(manual_input)
                if calculation_result is not None:
                    print(f"手动输入结果: {manual_input}，计算结果: {calculation_result}")
                    return calculation_result
                else:
                    print("错误: 无法计算手动输入的表达式。")
            else:
                print("输入格式无效，请重新输入类似 '1*6=' 的表达式。")
    return None


if __name__ == "__main__":
    # 弹出文件选择窗口
    Tk().withdraw()  # 隐藏主窗口
    print("请选择验证码图片文件...")
    image_path = askopenfilename(title="选择验证码图片", filetypes=[("图片文件", "*.png *.jpg *.jpeg")])

    if image_path:
        print(f"已选择图片文件: {image_path}")
        process_image(image_path)
    else:
        print("未选择任何文件，程序退出。")
