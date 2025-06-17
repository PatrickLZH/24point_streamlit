import re
import random
import itertools
import streamlit as st

# 计算表达式组合
def all_operations_combine(cards):
    c1, c2, c3, c4 = cards
    operations = ['+', '-', '*', '/']
    expressions = []
    for ops in itertools.product(operations, repeat=3):  # 笛卡尔积
        op1, op2, op3 = ops
        expressions.append(f'{c1}{op1}({c2}{op2}({c3}{op3}{c4}))')
        expressions.append(f'{c1}{op1}(({c2}{op2}{c3}){op3}{c4})')
        expressions.append(f'({c1}{op1}{c2}){op2}({c3}{op3}{c4})')
        expressions.append(f'({c1}{op1}({c2}{op2}{c3})){op3}{c4}')
        expressions.append(f'(({c1}{op1}{c2}){op2}{c3}){op3}{c4}')
    return expressions

def all_operations_combine_with_number_exchange(cards):
    all_results = []
    for cards_exchange in itertools.permutations(cards):  # 排列组合
        all_results += all_operations_combine(cards_exchange)
    return set(all_results)

# 解答函数
def answer_24_point(cards):
    result = None
    for exp in all_operations_combine_with_number_exchange(cards):
        try:
            if round(eval(exp), 1) == 24:
                result = exp
                break
        except ZeroDivisionError:
            continue
    else:
        result = '无解'
    return result

# 生成题目
def generate_question():
    cards = [random.randint(1, 10) for _ in range(4)]
    return f"{','.join(map(str, cards))}"

# 检查答案
def check_answer(cards_str, user_exp):
    try:
        cards = sorted(list(map(int, re.findall(r'\b\d+\b', cards_str))))
        card_user = sorted(list(map(int, re.findall(r'\b\d+\b', user_exp))))
        if user_exp.strip() == '无解' and answer_24_point(cards) == '无解':
            return "✅ 回答正确！"
        elif user_exp.strip() == '无解' and answer_24_point(cards) != '无解':
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) != 24:
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) == 24 and cards != card_user:
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) == 24 and cards == card_user:
            return "✅ 回答正确！"
    except ZeroDivisionError:
        return "⚠ 出现除零错误"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "⚠ 输入表达式格式错误"

# 显示参考答案
def show_reference(cards_str):
    cards = list(map(int, cards_str.split(',')))
    solution = answer_24_point(cards)
    return f"参考答案：{solution}"

# Streamlit UI 配置
st.markdown("# 计算24点小游戏")

if 'question' not in st.session_state:
    st.session_state.question = ""
if 'show_check' not in st.session_state:
    st.session_state.show_check = False
if 'show_ref' not in st.session_state:
    st.session_state.show_ref = False

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("生成新题目"):
        st.session_state.question = generate_question()
        st.session_state.show_check = True
        st.session_state.show_ref = True
        st.rerun()

with col2:
    question_output = st.text_input("题目区", value=st.session_state.question, disabled=True)

user_input = st.text_input("输入你的算式，例如：(3+3)*(8-4) 或者 无解")

if st.session_state.show_check and st.button("提交验证"):
    result = check_answer(st.session_state.question, user_input)
    st.text_area("结果反馈", value=result, height=100)

if st.session_state.show_ref and st.button("显示参考答案"):
    reference = show_reference(st.session_state.question)
    st.text_area("参考答案", value=reference, height=100)