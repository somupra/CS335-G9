import lexrules
import ply.lex as lex

if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
    with open(sys.argv[1]) as f:
        input = f.read()

    lexer.input(input)

    while(1):
        tok = lexer.token()
        if not tok:
            break

        col = lexrules.find_column(input, tok)
        print(tok.type, tok.value, tok.lineno, col)