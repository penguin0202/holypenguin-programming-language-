from StatementTypes import *
from ExpressionTypes import *
from TOKEN_TYPES import *

class Transpiler(): 
    def transpile_expression(self, expression: Expression) -> str:
        match expression: 
            case IntLiteralExpression(): 
                return expression.int_literal
            case BoolLiteralExpression(): 
                if expression.bool_literal == "true": 
                    return "True"
                else: 
                    return "False"
            case IdentifierExpression(): 
                return expression.name
            case NegateExpression(): 
                return "(-(" + self.transpile_expression(expression.operand) + ")"
            case NotExpression(): 
                return "(not(" + self.transpile_expression(expression.operand) + ")"
            case AssignmentExpression(): 
                return self.transpile_expression(expression.lvalue) + "=" + self.transpile_expression(expression.rvalue)
            case BinaryExprExpression(): 
                op_out_dict = {
                    TokenType.ADD: "+",
                    TokenType.SUB: "-",
                    TokenType.MUL: "*",
                    TokenType.DIV: "/",
                    TokenType.MOD: "%",
                    TokenType.AND: "and",
                    TokenType.OR: "or",
                    TokenType.LESS_THAN: "<",
                    TokenType.LESS_THAN_OR_EQUAL_TO: "<=",
                    TokenType.GREATER_THAN: ">", 
                    TokenType.GREATER_THAN_OR_EQUAL_TO: ">=",
                    TokenType.EQUAL_TO: "==", 
                    TokenType.NOT_EQUAL_TO: "!=",
                }
                return "(" + self.transpile_expression(expression.left) + op_out_dict[expression.operator] + self.transpile_expression(expression.right) + ")"

    def transpile_statement(self, statement: Statement) -> str: 
        match statement: 
            case ModuleStatement(): 
                return "".join(self.transpile_statement(statement) + "\n" for statement in statement.code)
            case BlockStatement(): 
                return "".join("\t" + self.transpile_statement(statement) + "\n" for statement in statement.code)
            case IfStatement():
                return "if " + self.transpile_expression(statement.condition) + ": \n" + self.transpile_statement(statement.statement)
            case IfElseStatement():
                return "if " + self.transpile_expression(statement.condition) + ": \n" + self.transpile_statement(statement.if_statement) \
                    + "else: \n" + self.transpile_statement(statement.else_statement)
            case WhileStatement():
                return "while " + self.transpile_expression(statement.condition) + ": \n" + self.transpile_statement(statement.statement)
            case BreakStatement():
                return "break"
            case IntVarDeclStatement():
                return statement.name.value + ":int=0"
            case BoolVarDeclStatement():
                return statement.name.value + ":bool=False"
            case ExpressionStatement():
                return self.transpile_expression(statement.expression)
            case EOFStatement():
                raise ValueError("EOFStatement not supported")