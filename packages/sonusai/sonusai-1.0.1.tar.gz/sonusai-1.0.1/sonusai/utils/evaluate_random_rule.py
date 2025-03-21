def evaluate_random_rule(rule: str) -> str | float:
    """Evaluate 'rand' directive

    :param rule: Rule
    :return: Resolved value
    """
    import re
    from random import uniform

    rand_pattern = re.compile(r"rand\(([-+]?(\d+(\.\d*)?|\.\d+)),\s*([-+]?(\d+(\.\d*)?|\.\d+))\)")

    def rand_repl(m):
        return f"{uniform(float(m.group(1)), float(m.group(4))):.2f}"  # noqa: S311

    return eval(re.sub(rand_pattern, rand_repl, rule))  # noqa: S307
