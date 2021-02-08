import lexrules
import ply.lex as lex

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

def get_max_col_width(output):
    width = 0
    for op in output:
        for str in op:
            width = max(width, len(str))

    return width+1

if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
    with open(sys.argv[1]) as f:
        input = f.read()

    lexer.input(input)
    output = []
    while(1):
        tok = lexer.token()
        if not tok:
            break

        col = find_column(input, tok)
        output.append([str(tok.type), str(tok.value), str(tok.lineno), str(col)])

    max_col_width = get_max_col_width(output)
    row_format = "{:<"+ str(max_col_width + 3) +"}" 
    
    if(output): row_format = row_format * (len(output[0])+1)
    else: exit()

    print('-'*((max_col_width + 2)*4))
    header = ['TOKEN', 'LEXEME', 'ROW', 'COLUMN']
    header_string = row_format.format("", *header)
    print(header_string.strip())
    print('-'*((max_col_width + 2)*4))

    for op in output:
        op_string = row_format.format("", *op)
        print(op_string.strip())