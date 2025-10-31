import random
import math
import regex
import asyncio
import os
import matplotlib.pyplot as plt
from mistralai import Mistral
from mistralai.models import UserMessage
from pdf2image import convert_from_path

INT_RANGE = 42 # range of randomly generated integers (note: should be >1)
FRACTION_COEFF_ODDS = 0.9 # odds of coefficient being a fraction
FRACTION_POWER_ODDS = 0.66 # odds of power being a fraction
FRACTION_POLY_ODDS = 0.4 # odds of randomly generated x term including fractions
POWER_ISANNOYING_ODDS = 0.55 # odds of power being unpleasant (not single integers)
POWER_ISNEGATIVE_ODDS = 0.73 # odds of power being negative
INT_OPERATION_ODDS = 0.68 # odds of operation involving integers only
CONSTANT_OPERATION_ODDS = 0.55 # odds of operation involving constants (not necessarily integers, but fractions)
NICEX_OPERATION_ODDS = 0.37 # odds of x being of the form ax^b where a, b are integers
NICE_EXPO_ODDS = 0.7 # odds of exponential power being integer only
NICE_LOG_ODDS = 0.75 # odds of logarithm being the natural log
FRACTION_EXPR_ODDS = 0.8 # odds of generated expression being put through a fraction if difficulty isn't medium or hard

async def solve_problem(problem: str) -> str:
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-medium-latest"

    client = Mistral(api_key=api_key)
    res = await client.chat.complete_async(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a master of differentiation, your task is to differentiate a user-provided "
                           "mathematical expression, which is typically given in LaTeX form. You do not to provide "
                           "any intermediate steps, working out, just concern yourself with the final answer. The final "
                           "answer should be in the form of <answer>. <answer> should be in MathJax form, "
                           "such that <answer> can be rendered appropriately. Refrain, as much as possible from adding "
                           "further clarification in textual word such as stating 'The answer is..', 'The derivative is..', "
                           "'Here\'s the answer' etc."
            },
            {
                "role": "user",
                "content": "What is the derivative of " + problem + " ?"
            }
        ]
    )

    solution = res.choices[0].message.content
    return solution

def latex_to_png(latex_str: str) -> str:
    """

    :param latex_str: LaTeX string to be converted to an image.
    :return: the path of the final image
    """
    fig = plt.figure()
    plt.axis("off")
    plt.text(0.5, 0.5, f"${latex_str}$", size=50, ha="center", va="center")
    pdf_path = "static/result.pdf"
    png_path = "static/result.png"
    plt.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.4)
    plt.close(fig)
    images = convert_from_path(pdf_path)
    images[0].save(png_path, "PNG")
    return png_path


def frac_helper(mode: str) -> str:
    """
    Helper function to generate fractions within LaTeX
    :mode: str, specifies \\frac or \dfrac. Can be either "dfrac" or "frac"
    :return: LaTeX string, which represents the (simplified) fraction
    """
    num = random.randint(-INT_RANGE, INT_RANGE)
    denom = random.randint(1, INT_RANGE)
    if num == denom:
        num += random.randint(1, denom - 1)
    gcd = math.gcd(num, denom)
    num, denom = num // gcd, denom // gcd
    if denom == 1:
        if num == 1:
            return ""
        else:
            return str(num)
    else:
        f = ""
        if mode == "frac":
            f = "\\frac{" + str(num) + "}{" + str(denom) + "}"
            if regex.search("\\\\frac\{-\d+\}\{\d+\}", f):
                return "-" + f.replace("-", "")
        if mode == "dfrac":
            f = "\dfrac{" + str(num) + "}{" + str(denom) + "}"
            if regex.search("\\\\dfrac\{-\d+\}\{\d+\}", f):
                return "-" + f.replace("-", "")
        return f


def random_x(coefficient_mode: str) -> str:
    """
    :param coefficient_mode: This determines whether the coefficient is frac or dfrac
    :return: Any exponent, multiple version of x in LaTeX.
    """
    p = random.random()
    if p < FRACTION_POLY_ODDS:
        lat_coefficient = str(random.randint(-INT_RANGE, INT_RANGE))
        lat_power = str(random.randint(-INT_RANGE, INT_RANGE))
        if p >= FRACTION_COEFF_ODDS:
            if coefficient_mode == "dfrac":
                lat_coefficient = frac_helper("dfrac")
            if coefficient_mode == "frac":
                lat_coefficient = frac_helper("frac")
        if p < FRACTION_POWER_ODDS:
            lat_power = frac_helper("frac")
    else:
        lat_coefficient = str(random.randint(-INT_RANGE, INT_RANGE))
        lat_power = str(random.randint(-INT_RANGE, INT_RANGE))
    if lat_coefficient == "1":
        lat_coefficient = ""
    if lat_coefficient == "-1":
        lat_coefficient = "-"
    if lat_coefficient == "0":
        return "1"
    if lat_power == "1":
        lat_power = ""
    if lat_power == "0" or regex.search("\\\\dfrac\{0\}\{\d+\}", lat_power):
        if regex.search("\\\\dfrac\{-\d+\}\{\d+\}", lat_coefficient):
            lat_coefficient = "-" + lat_coefficient.replace("-", "")
        return lat_coefficient
    return lat_coefficient + "x^{" + lat_power + "}"


def random_power(expression: str, brackets=True) -> str:
    """
    :param brackets: True if u want brackets, false if nah
    :param expression: str, in LaTeX
    :return: str, the expression in LaTeX raised to an arbitrary power
    """
    p1 = random.random()
    p2 = random.random()
    s1 = "{"
    s2 = "}^{"
    if brackets:
        s1 = "{\\left("
        s2 = "\\right)}^{"
    if p1 > POWER_ISANNOYING_ODDS:
        if p2 > FRACTION_POWER_ODDS:
            return s1 + expression + s2 + frac_helper("frac") + "}"
        elif p2 > POWER_ISNEGATIVE_ODDS:
            return s1 + expression + s2 + str(random.randint(-10 * INT_RANGE, - (INT_RANGE // 2))) + "}"
        else:
            return s1 + expression + s2 + str(random.randint(INT_RANGE, 99)) + "}"

    else:
        if p2 >= POWER_ISNEGATIVE_ODDS:
            return s1 + expression + s2 + str(random.randint(- INT_RANGE, - (INT_RANGE// 2))) + "}"
        else:
            return s1 + expression + s2 + str(random.randint(INT_RANGE // 2, INT_RANGE)) + "}"



def random_trig(expression: str, raised=True) -> str:
    """

    :param expression: Expression that is already in LaTeX
    :param raised: Indicates whether you want the trig to be raised to a power
    :return: Expression, that is wrapped in the trig
    """
    trigs = ["\\sin", "\\cos", "\\tan", "\\csc", "\\sec", "\\cot", "\\arcsin",
             "\\arccos", "\\arctan",
             # "\\text{arcsec}", "\\text{arccsc}", "\\text{arccot}"
             ]
    trig = random.choice(trigs)
    if raised:
        return random_power(trig, False) + f"\\left({expression}\\right)"
    else:
        return trig + f"\\left({expression}\\right)"


def random_operation(expression: str) -> str:
    """
    We want to add or subtract a random number (or random "x" term) to the expression
    :param expression: str, the expression inn LaTeX
    :return: the final expression, which is slightly modified.
    """
    p1 = random.random()
    p2 = random.random()
    operations = ["+", "-"]
    op = random.choice(operations)
    if p1 > CONSTANT_OPERATION_ODDS:
        if p2 > INT_OPERATION_ODDS:
            return expression + op + str(random.randint(1, INT_RANGE))
        else:
            frac = frac_helper("frac")
            if op == "+" and frac[0] == "-":
                frac = frac[1:]
                op = "-"
            elif op == "-" and frac[0] == "-":
                frac = frac[1:]
                op = "+"
            return expression + op + frac
    else:
        signs = ["", "-"]
        sign = random.choice(signs)
        if p2 > NICEX_OPERATION_ODDS:
            return (expression + op + str(random.randint(1, INT_RANGE)) +
                    "x^{" + sign + str(random.randint(1, INT_RANGE)) + "}").replace("1x", "")
        else:
            x_term = random_x("frac")
            if op == "+" and x_term[0] == "-":
                x_term = x_term[1:]
                op = "-"
            elif op == "-" and x_term[0] == "-":
                x_term = x_term[1:]
                op = "+"
            return expression + op + x_term


def random_exponential(expression: str) -> str:
    """
    Make the expression the base of some number > 1 to guarantee that it is well-defined.
    :param expression:
    :return:
    """
    p = random.random()
    if p > NICE_EXPO_ODDS:
        return str(random.randint(2, INT_RANGE)) + "^{" + expression + "}"
    else:
        return f"{random.uniform(1.1, INT_RANGE * 2):.2f}" + "^{" + expression + "}"


def random_logarithm(expression: str) -> str:
    """
    Make the expression inside a logarithm
    :param expression:
    :return:
    """
    p = random.random()
    pos_expression = expression[1:] if expression[0] == '-' else expression

    if p > NICE_LOG_ODDS:
        return "\\ln" + " {\\left(" + pos_expression + "\\right)}"
    else:
        return "\\log_{" + str(random.randint(2, INT_RANGE * 2)) + "}{\\left(" + pos_expression + "\\right)}"


def random_product(expression: str) -> str:
    """
    Multiply expression by a random expression
    :param expression:
    :return:
    """
    expressions = [random_logarithm, random_exponential, random_operation, random_trig, random_power]
    new_expression = random.choice(expressions)
    return expression + new_expression(random_x("frac"))


def random_expression(difficulty: str) -> str:
    """
    :param difficulty: str that indicates the difficulty level, either 'baby', 'easy', 'medium', 'hard', 'ruSure'
    :return: the expression, in LaTeX.
    """
    difficulties = {"baby": 1,
                    "easy": random.randint(1, 3),
                    "medium": random.randint(4, 6),
                    "hard": random.randint(8, 12),
                    "ruSure": 20,
                    "dev": 25
                    }
    n = difficulties[difficulty]
    mutators = [random_logarithm, random_exponential, random_operation, random_trig, random_power, random_product]
    x_term = random_x("frac")
    for _ in range(n):
        p = random.random()
        mutator = random.choice(mutators)
        if mutator is random_trig and (difficulty == "easy" or difficulty == 'baby'):
            x_term = mutator(x_term, False)
        elif p > 0.80:
            if difficulty == "easy" or difficulty == 'baby':
                x_term = mutator(x_term)
            else:
                x_term = "\\dfrac{" + x_term + "}{" + mutator(random_x("frac")) + "}"
        else:
            x_term = mutator(x_term)
    return x_term

def calc_gen(difficulty: str) -> None:
    """
    Original "main" function. It creates an image and pdf
    of the generated latex expression.

    :param difficulty:
    :return:
    """
    x = random_expression(difficulty)
    with open("static/result.txt", "w") as f:
        f.write(x + "\n")
        f.write(x.replace("\\left", "").replace("\\right", "").replace("^{}", ""))
    latex_to_png(x)

def calc_gen_text(difficulty: str) -> str:
    """
    Modified calc_gen to return the latex string, albeit slightly
    reformatted.

    :param difficulty:
    :return:
    """
    x = random_expression(difficulty)
    return x.replace("^{}", "")

if __name__ == "__main__":
    calc_gen("hard")
