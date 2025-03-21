def convert_line_to_list(line, separator=';', prefix='', suffix=''):
    result = []
    for l in line.split(separator):
        result.append(prefix + l + suffix)
    return result