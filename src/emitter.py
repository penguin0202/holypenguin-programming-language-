from TYPES.STATEMENT_TYPES import *
from TYPES.EXPRESSION_TYPES import *
from TYPES.TOKEN_TYPES import *

class Emitter(): 
    def emit_expression(self, expression: Expression) -> str:
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
                return "(-(" + self.emit_expression(expression.operand) + ")"
            case NotExpression(): 
                return "(not(" + self.emit_expression(expression.operand) + ")"
            case AssignmentExpression(): 
                return self.emit_expression(expression.lvalue) + "=" + self.emit_expression(expression.rvalue)
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
                return "(" + self.emit_expression(expression.left) + op_out_dict[expression.operator] + self.emit_expression(expression.right) + ")"

    def emit_statement(self, statement: Statement) -> str: 
        match statement: 
            case ModuleStatement(): 
                return "".join(self.emit_statement(statement) + "\n" for statement in statement.code)
            case BlockStatement(): 
                return "".join("\t" + self.emit_statement(statement) + "\n" for statement in statement.code)
            case IfStatement():
                return "if " + self.emit_expression(statement.condition) + ": \n" + self.emit_statement(statement.statement)
            case IfElseStatement():
                return "if " + self.emit_expression(statement.condition) + ": \n" + self.emit_statement(statement.if_statement) \
                    + "else: \n" + self.emit_statement(statement.else_statement)
            case WhileStatement():
                return "while " + self.emit_expression(statement.condition) + ": \n" + self.emit_statement(statement.statement)
            case BreakStatement():
                return "break"
            case IntVarDeclStatement():
                return statement.name.value + ":int=0"
            case BoolVarDeclStatement():
                return statement.name.value + ":bool=False"
            case ExpressionStatement():
                return self.emit_expression(statement.expression)
            case EOFStatement():
                raise ValueError("EOFStatement not supported")