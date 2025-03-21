def print_in_color(
        text, style=None, updating=False, dont_print=False,
        red=False,
        green=False,
        blue=False,
        orange=False,
        yellow=False,
        purple=False,
    ):

    if red:
        color = '255;0;0'
    elif green:
        color = '0;255;0'
    elif blue:
        color = '0;0;255'
    elif orange:
        color = '255;155;0'
    elif yellow:
        color = '255;255;0'
    elif purple:
        color = '155;0;255'
    else:
        color = '255;255;255'

    def get_style(styles):
        if styles == None:
            return ''
        styles = list(styles)
        STYLES = {
            'b': 1,
            'f': 2,
            'i': 3,
            'u': 4,
            's': 9,
        }
        res = ''
        for style in styles:
            if style not in STYLES:
                return ''
            res += ';' + str(STYLES.get(style))
        return res

    style = get_style(style)
    if updating:
        updating_end = '\r'
    else:
        updating_end = None

    res = f"\x1B[38;2;{color}{style}m{text}\x1B[0m"

    if dont_print:
        return res
    print(res, end=updating_end)

if __name__ == '__main__':
    red = print_in_color('test', purple=1)
