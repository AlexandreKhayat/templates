UNITS = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
         "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
         "dix-sept", "dix-huit", "dix-neuf"]
TENS = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]

def under100(n):
    if n < 20:
        return UNITS[n]
    t, u = divmod(n, 10)
    if t == 7 or t == 9:
        t -= 1
        u += 10
    word = TENS[t]
    if u == 0:
        if t in (8,):
            word += "s"
        return word
    elif u == 1 and t not in (8, 9) and t != 7:
        word += "-et-un"
    else:
        word += "-" + UNITS[u]
    return word

def under1000(n, final=True):
    c, r = divmod(n, 100)
    parts = []
    if c > 0:
        if c == 1:
            parts.append("cent")
        else:
            parts.append(UNITS[c] + " cent" + ("s" if (r == 0 and final) else ""))
    if r > 0:
        parts.append(under100(r))
    return " ".join(parts) if parts else "zéro"

def num2fr(n):
    n = int(n)
    if n == 0:
        return "zéro"
    neg = n < 0
    n = abs(n)
    parts = []
    millions, n = divmod(n, 1000000)
    thousands, n = divmod(n, 1000)
    rest = n
    if millions:
        if millions == 1:
            parts.append("un million")
        else:
            parts.append(under1000(millions, final=False) + " millions")
    if thousands:
        if thousands == 1:
            parts.append("mille")
        else:
            parts.append(under1000(thousands, final=False) + " mille")
    if rest or not parts:
        parts.append(under1000(rest, final=True))
    result = " ".join(parts)
    return ("moins " if neg else "") + result

if __name__ == "__main__":
    for v in [500000, 21000, 50000, 25000, 400000, 25, 3, 2, 0]:
        print(v, "->", num2fr(v))
