import sys

def p_primary_expression(p):
    '''
    primary_expression : ID
	               | CHAR_CONST
                       | NUMBER
	               | OP expression CP
    '''
  
def p_postfix_expression(p):
    '''
    postfix_expression : primary_expression
	               | postfix_expression OSP expression CSP
                       | postfix_expression OP CP
                       | postfix_expression OP argument_expression_list CP
                       | postfix_expression DOT ID
                       | postfix_expression ARROW ID
                       | postfix_expression INCREMENT
                       | postfix_expression DECREMENT
    '''

def p_argument_expression_list(p):
  '''
  argument_expression_list : assignment_expression
                           | argument_expression_list COMMA assignment_expression
  '''

def p_unary_expression(p):
  '''
  unary_expression : postfix_expression
	           | INCREMENT unary_expression
                   | DECREMENT unary_expression
                   | unary_operator cast_expression
                   | SIZEOF unary_expression
                   | SIZEOF OP type_name CP
  '''

def p_unary_operator(p):
  '''
  unary_operator : B_AND
	         | MULTIPLY
                 | ADD
                 | SUBTRACT
                 | B_NOT
                 | NOT
  '''

def p_cast_expression(p):
  '''
  cast_expression : unary_expression
	          | OP type_name CP cast_expression
  '''

def p_multiplicative_expression(p):
  '''
  multiplicative_expression : cast_expression
	                    | multiplicative_expression MULTIPLY cast_expression
	                    | multiplicative_expression DIVIDE cast_expression
	                    | multiplicative_expression MOD cast_expression
  '''

def p_additive_expression(p):
  '''
  additive_expression : multiplicative_expression 
                      | additive_expression ADD multiplicative_expression
	              | additive_expression SUBTRACT multiplicative_expression
  '''

def p_shift_expression(p):
  '''
  shift_expression : additive_expression
	           | shift_expression LSHIFT additive_expression
                   | shift_expression RSHIFT additive_expression
  '''
  
def p_relational_expression(p):
  '''
  relational_expression : shift_expression
	                | relational_expression LT shift_expression
                        | relational_expression GT shift_expression
                        | relational_expression LEQ shift_expression
                        | relational_expression GEQ shift_expression
  '''
  
def p_equality_expression(p):
  '''
  equality_expression : relational_expression
                      | equality_expression EQUAL relational_expression
	              | equality_expression NEQ relational_expression
  '''

def p_and_expression(p):
  '''
  and_expression : equality_expression
	         | and_expression B_AND equality_expression
  '''

def p_exclusive_or_expression(p):
    '''
    exclusive_or_expression : and_expression
                            | exclusive_or_expression XOR and_expression
    '''

def p_inclusive_or_expression(p):
    '''
    inclusive_or_expression : exclusive_or_expression
                            | inclusive_or_expression B_OR exclusive_or_expression
    '''
    
def p_logical_and_expression(p):
    '''
    logical_and_expression : inclusive_or_expression
                           | logical_and_expression AND inclusive_or_expression
    '''

def p_logical_or_expression(p):
    '''
    logical_or_expression : logical_and_expression
                          | logical_or_expression OR logical_and_expression
    '''

def p_conditional_expression(p):
    '''
    conditional_expression : logical_or_expression
                           | logical_or_expression TERNARYOP expression COLON conditional_expression
    '''

def p_assignment_expression(p):
    '''
    assignment_expression : conditional_expression
                          | unary_expression assignment_operator assignment_expression    
    '''

def p_assignment_operator(p):
    '''
    assignment_operator : ASSIGN
                        | MUL_ASSIGN
                        | DIV_ASSIGN
                        | MOD_ASSIGN
                        | ADD_ASSIGN
                        | SUB_ASSIGN
                        | LEFT_ASSIGN
                        | RIGHT_ASSIGN
                        | AND_ASSIGN
                        | XOR_ASSIGN
                        | OR_ASSIGN
    '''

def p_expression(p):
    '''
    expression : assignment_expression
               | expression COMMA assignment_expression
    '''

def p_constant_expression(p):
    '''
    constant_expression : conditional_expression
    '''

def p_declaration(p):
    '''
    declaration : declaration_specifiers SEMICOLON
	| declaration_specifiers init_declarator_list SEMICOLON
    '''
    
def p_declaration_specifiers(p):
    '''
    declaration_specifiers : storage_class_specifier
                           | storage_class_specifier declaration_specifiers
                           | type_specifier
                           | type_specifier declaration_specifiers
                           | type_qualifier
                           | type_qualifier declaration_specifiers
    '''

def p_init_declarator_list(p):
    '''
    init_declarator_list : init_declarator
                         | init_declarator_list COMMA init_declarator
    '''

def p_init_declarator(p):
    '''
    init_declarator : declarator
                    | declarator ASSIGN initializer
    '''

def p_storage_class_specifier(p):
    '''
    storage_class_specifier : TYPEDEF
                            | EXTERN
                            | STATIC
                            | AUTO
                            | REGISTER
    '''

def p_type_specifier(p):
    '''
    type_specifier : VOID
                   | CHAR
                   | SHORT
                   | INT
                   | LONG
                   | FLOAT
                   | DOUBLE
                   | SIGNED
                   | UNSIGNED
                   | struct_or_union_specifier
                   | enum_specifier
                   | TYPE_NAME
    '''

def p_struct_or_union_specifier(p):
    '''
    struct_or_union_specifier : struct_or_union ID OCP struct_declaration_list CCP
                              | struct_or_union OCP struct_declaration_list CCP
                              | struct_or_union ID
    '''

def p_struct_or_union(p):
    '''
    struct_or_union : STRUCT
                    | UNION
    '''

def p_struct_declaration_list(p):
    '''
    struct_declaration_list : struct_declaration
                            | struct_declaration_list struct_declaration
    '''

def p_struct_declaration(p):
    '''
    struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
    '''

def p_specifier_qualifier_list(p):
    '''
    specifier_qualifier_list : type_specifier specifier_qualifier_list
                             | type_specifier
                             | type_qualifier specifier_qualifier_list
                             | type_qualifier
    '''

def p_struct_declarator_list(p):
    '''
    struct_declarator_list : struct_declarator
                           | struct_declarator_list COMMA struct_declarator
    '''

def p_struct_declarator(p):
    '''
    struct_declarator : declarator
                      | COLON constant_expression
                      | declarator COLON constant_expression
    '''

def p_enum_specifier(p):
    '''
    enum_specifier : ENUM OCP enumerator_list CCP
                   | ENUM ID OCP enumerator_list CCP
                   | ENUM ID
    '''

def p_enumerator_list(p):
    '''
    enumerator_list : enumerator
                    | enumerator_list COMMA enumerator
    '''

def p_enumerator(p):
    '''
    enumerator : ID
               | ID ASSIGN constant_expression
    '''

def p_type_qualifier(p):
    '''
    type_qualifier : CONST
                   | VOLATILE
    '''
	
def p_declarator(p):
    '''
    declarator : pointer direct_declarator
               | direct_declarator
    '''

def p_direct_declarator(p):
    '''
    direct_declarator : ID
                      | OP declarator CP
                      | direct_declarator OSP constant_expression CSP
                      | direct_declarator OSP CSP
                      | direct_declarator OP parameter_type_list CP
                      | direct_declarator OP identifier_list CP
                      | direct_declarator OP CP
    '''

def p_pointer(p):
    '''
    pointer : MULTIPLY
            | MULTIPLY type_qualifier_list
            | MULTIPLY pointer
            | MULTIPLY type_qualifier_list pointer
    '''

def p_type_qualifier_list(p):
    '''
    type_qualifier_list : type_qualifier
                        | type_qualifier_list type_qualifier
    '''

def p_parameter_type_list(p):
    '''
    parameter_type_list : parameter_list
                        | parameter_list COMMA ELLIPSIS
    '''

def p_parameter_list(p):
    '''
    parameter_list : parameter_declaration
                   | parameter_list COMMA parameter_declaration
    '''

def p_parameter_declaration(p):
    '''
    parameter_declaration : declaration_specifiers declarator
                          | declaration_specifiers abstract_declarator
                          | declaration_specifiers
    '''
	
def p_identifier_list(p):
    '''
    identifier_list : ID
                    | identifier_list COMMA ID
    '''

def p_type_name(p):
    '''
    type_name : specifier_qualifier_list
              | specifier_qualifier_list abstract_declarator
    '''

def p_abstract_declarator(p):
    '''
    abstract_declarator : pointer
                        | direct_abstract_declarator
                        | pointer direct_abstract_declarator
    '''

def p_direct_abstract_declarator(p):
    '''
    direct_abstract_declarator : OP abstract_declarator CP
                               | OSP CSP
                               | OSP constant_expression CSP
                               | direct_abstract_declarator OSP CSP
                               | direct_abstract_declarator OSP constant_expression CSP
                               | OP CP
                               | OP parameter_type_list CP
                               | direct_abstract_declarator OP CP
                               | direct_abstract_declarator OP parameter_type_list CP
    '''

def p_initializer(p):
    '''
    initializer : assignment_expression
                | OCP initializer_list CCP
                | OCP initializer_list COMMA CSP
    '''

def p_initializer_list(p):
    '''
    initializer_list : initializer
                     | initializer_list COMMA initializer
    '''

def p_statement(p):
    '''
    statement : labeled_statement
              | compound_statement
              | expression_statement
              | selection_statement
              | iteration_statement
              | jump_statement
    '''

def p_labeled_statement(p):
    '''
    labeled_statement : ID COLON statement
                      | CASE constant_expression COLON statement
                      | DEFAULT COLON' statement
    '''

def p_compound_statement(p):
    '''
    compound_statement : OCP CCP
                       | OCP statement_list CCP
                       | OCP declaration_list CCP
                       | OCP declaration_list statement_list CCP
    '''

def p_declaration_list(p):
    '''
    declaration_list : declaration
                     | declaration_list declaration
    '''

def p_statement_list(p):
    '''
    statement_list : statement
                   | statement_list statement
    '''

def p_expression_statement(p):
    '''
    expression_statement : SEMICOLON
                         | expression SEMICOLON
    '''

def p_selection_statement(p):
    '''
    selection_statement : IF OP expression CP statement
                        | IF OP expression CP statement ELSE statement
                        | SWITCH OP expression CP statement
    '''
	
def p_iteration_statement(p):
    '''
    iteration_statement : WHILE OP expression CP statement
                        | DO statement WHILE OP expression CP SEMICOLON
                        | FOR OP expression_statement expression_statement CP statement
                        | FOR OP expression_statement expression_statement expression CP statement
    '''

def p_jump_statement(p):
    '''
    jump_statement : GOTO ID SEMICOLON
                   | CONTINUE SEMICOLON
                   | BREAK SEMICOLON
                   | RETURN SEMICOLON
                   | RETURN expression SEMICOLON
    '''

def p_translation_unit(p):
    '''
    translation_unit : external_declaration
                     | translation_unit external_declaration
    '''

def p_external_declaration(p):
    '''
    external_declaration : function_definition
                         | declaration
    '''
	
def p_function_definition(p):
    '''
    function_definition : declaration_specifiers declarator declaration_list compound_statement
                        | declaration_specifiers declarator compound_statement
                        | declarator declaration_list compound_statement
                        | declarator compound_statement
    '''

def p_error(p):
    print "Syntax Error"
    sys.exit()
