import random
import math
import regex
import matplotlib.pyplot as plt
from pdf2image import convert_from_path


def latex_to_png(latex_str: str) -> str:
    """

    :param latex_str: LaTeX string to be converted to an image.
    :return: the path of the final image
    """
    fig = plt.figure()
    plt.axis("off")
    plt.text(0.5, 0.5, f"${latex_str}$", size=50, ha="center", va="center")
    pdf_path = "./result.pdf"
    png_path = "./result.png"
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
    num = random.randint(-42, 42)
    denom = random.randint(1, 42)
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
    if p < 0.9:
        lat_coefficient = str(random.randint(-42, 42))
        lat_power = str(random.randint(-10, 10))
        if p >= 0.5:
            if coefficient_mode == "dfrac":
                lat_coefficient = frac_helper("dfrac")
            if coefficient_mode == "frac":
                lat_coefficient = frac_helper("frac")
            if p < 0.66:
                lat_power = frac_helper("frac")
    else:
        lat_coefficient = str(random.randint(-10, 10))
        lat_power = str(random.randint(-6, 6))
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
    if p1 > 0.7:
        if p2 > 0.66:
            return s1 + expression + s2 + frac_helper("frac") + "}"
        elif p2 < 0.78:
            return s1 + expression + s2 + str(random.randint(10, 99)) + "}"
        else:
            return s1 + expression + s2 + str(random.randint(-101, -11)) + "}"
    else:
        if p2 >= 0.5:
            return s1 + expression + s2 + str(random.randint(2, 9)) + "}"
        else:
            return s1 + expression + s2 + str(random.randint(-9, -1)) + "}"


def random_trig(expression: str, raised=True) -> str:
    """

    :param expression: Expression that is already in LaTeX
    :param raised: Indicates whether you want the trig to be raised to a power
    :return: Expression, that is wrapped in the trig
    """
    trigs = ["\\sin", "\\cos", "\\tan", "\\csc", "\\sec", "\\cot", "\\arcsin",
             "\\arccos", "\\arctan", "\\text{arcsec}", "\\text{arccsc}", "\\text{arccot}"]
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
    if p1 > 0.55:
        if p2 > 0.65:
            return expression + op + str(random.randint(1, 99))
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
        if p2 > 0.37:
            return (expression + op + str(random.randint(1, 85)) +
                    "x^{" + sign + str(random.randint(1, 85)) + "}")
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
    if p > 0.8:
        return f"{random.uniform(1.1, 87):.2f}" + "^{" + expression + "}"
    else:
        return str(random.randint(2, 98)) + "^{" + expression + "}"


def random_logarithm(expression: str) -> str:
    """
    Make the expression inside a logarithm
    :param expression:
    :return:
    """
    p = random.random()
    if p > 0.64:
        return "\\log_{" + str(random.randint(2, 87)) + "}{\\left(" + expression + "\\right)}"
    else:
        return "\\ln" + " {\\left(" + expression + "\\right)}"


def random_expression(difficulty: str) -> str:
    """
    :param difficulty: str that indicates the difficulty level, either 'baby', 'easy', 'medium', 'hard', 'ruSure'
    :return: the expression, in LaTeX.
    """
    mutators = [random_logarithm, random_exponential, random_operation, random_trig, random_power]
    difficulties = {"baby": 1,
                    "easy": random.randint(1, 3),
                    "medium": random.randint(4, 6),
                    "hard": random.randint(8, 12),
                    "ruSure": 20
                    }
    n = difficulties[difficulty]
    x_term = random_x("frac")
    for _ in range(n):
        p = random.random()
        mutator = random.choice(mutators)
        if mutator is random_trig and (difficulty == "easy" or difficulty == 'baby'):
            x_term = mutator(x_term, False)
        elif p > 0.85:
            if difficulty == "easy" or difficulty == 'baby':
                x_term = mutator(x_term)
            else:
                x_term = "\\dfrac{" + x_term + "}{" + mutator(random_x("frac")) + "}"
        else:
            x_term = mutator(x_term)
    return x_term


if __name__ == "__main__":
    x = random_expression("medium")
    with open("result.txt", "w") as f:
        f.write(x + "\n")
        f.write(x.replace("\\left", "").replace("\\right", "").replace("^{}", ""))
    latex_to_png(x)
