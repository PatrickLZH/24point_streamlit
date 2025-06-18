import re
import random
import itertools
import streamlit as st

# 初始化 N 的值
N = st.session_state.n_value if 'n_value' in st.session_state else 4
MAX = st.session_state.max_value if 'max_value' in st.session_state else 10
ANSWER = st.session_state.answer_value if 'answer_value' in st.session_state else 24
print(N, MAX, ANSWER)
def add_brace(cards):
    if len(cards) < 2: return [cards]
    if len(cards) == 2: 
        return [['(' + str(cards[0])] + [str(cards[1]) + ')']]
    cards_with_brace_list = []
    for i in range(1, len(cards)):
        prefix = cards[:i]
        prefixs = add_brace(prefix)
        tail = cards[i:]
        tails = add_brace(tail)
        for p, t in itertools.product(prefixs, tails):
            cards_with_brace = ['(' + p[0]] + p[1:] + t[:-1] + [t[-1]+ ')']
            cards_with_brace_list.append(cards_with_brace)
    return cards_with_brace_list

def join_op_with_brace_number(operators, with_brace):
    expression = with_brace[0]
    for i, op in enumerate(operators):
        expression += op + with_brace[i+1]
    return expression

def join_brace_to_expression(cards, ops):
    with_braces = add_brace(cards)
    exps = []
    for brace in with_braces:
        exp = join_op_with_brace_number(ops, brace)[1:-1]
        exps.append(exp)
    return exps

# 计算表达式组合
def all_operations_combine(cards):
    operations = ['+', '-', '*', '/']
    expressions = []
    for ops in itertools.product(operations, repeat=N-1):  # 笛卡尔积
        expression = join_brace_to_expression(cards, ops)
        expressions += expression
    return expressions

def all_operations_combine_with_number_exchange(cards):
    all_results = []
    for cards_exchange in itertools.permutations(cards):  # 排列组合
        all_results += all_operations_combine(list(cards_exchange))
    return set(all_results)

# 解答函数
def answer_n_point(cards):
    result = None
    for exp in all_operations_combine_with_number_exchange(cards):
        try:
            if round(eval(exp), 1) == ANSWER:
                result = exp
                break
        except ZeroDivisionError:
            continue
    else:
        result = '无解'
    return result

# 生成题目
def generate_question():
    cards = [random.randint(1, MAX) for _ in range(N)]
    return f"{','.join(map(str, cards))}"

# 检查答案
def check_answer(cards_str, user_exp):
    try:
        cards = sorted(list(map(int, re.findall(r'\b\d+\b', cards_str))))
        card_user = sorted(list(map(int, re.findall(r'\b\d+\b', user_exp))))
        if user_exp.strip() == '无解' and answer_n_point(cards) == '无解':
            return "✅ 回答正确！"
        elif user_exp.strip() == '无解' and answer_n_point(cards) != '无解':
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) != ANSWER:
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) == ANSWER and cards != card_user:
            return "❌ 回答错误，请再试试！"
        elif round(eval(user_exp.strip()), 1) == ANSWER and cards == card_user:
            return "✅ 回答正确！"
    except ZeroDivisionError:
        return "⚠ 出现除零错误"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "⚠ 输入表达式格式错误"

# 显示参考答案
def show_reference(cards_str):
    cards = list(cards_str.split(','))
    solution = answer_n_point(cards)
    return f"参考答案：{solution}"

# cards = ['6','6','6']
# print(answer_n_point(cards))

# Streamlit UI 配置
st.markdown("# 计算N点小游戏")
if 'n_value' not in st.session_state:
    st.session_state.n_value = N
if 'max_value' not in st.session_state:
    st.session_state.max_value = MAX
if 'answer_value' not in st.session_state:
    st.session_state.answer_value = ANSWER

if 'question' not in st.session_state:
    st.session_state.question = ""
if 'show_check' not in st.session_state:
    st.session_state.show_check = False
if 'show_ref' not in st.session_state:
    st.session_state.show_ref = False

# 添加输入框和确认按钮
with st.sidebar:
    st.header("参数设置")
    n_input = st.number_input("请输入卡牌数量", min_value=2, value=st.session_state.n_value)
    max_input = st.number_input("请输入卡牌的最大数值", min_value=1, value=st.session_state.max_value)
    answer_input = st.number_input("请输入目标答案", value=st.session_state.answer_value)

    if st.button("确认参数"):
        # 更新全局参数
        st.session_state.n_value = int(n_input)
        st.session_state.max_value = int(max_input)
        st.session_state.answer_value = int(answer_input)
        st.success("参数已更新！")
        st.session_state.question = ""
        st.session_state.show_check = False
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
