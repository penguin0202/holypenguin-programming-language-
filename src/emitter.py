from TYPES.STATEMENT_TYPES import *
from TYPES.EXPRESSION_TYPES import *
from TYPES.TOKEN_TYPES import *
from llvmlite import ir, binding

class Emitter(): 
    def __init__(self): 
        self.module = ir.Module(name="main")
        self.i32 = ir.IntType(32)
        self.i1 = ir.IntType(1)

        self.variables = {}
        self.loop_end_blocks = []

        func_type = ir.FunctionType(self.i32, [])
        self.function = ir.Function(
            self.module, func_type, name="main"
        )

        entry = self.function.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)
    def emit_expression(self, expression: Expression):
        match expression: 
            case IntLiteralExpression(): 
                return ir.Constant(self.i32, int(expression.int_literal))
            case BoolLiteralExpression(): 
                return ir.Constant(self.i1, int(expression.bool_literal == "true"))
            case IdentifierExpression(): 
                return self.builder.load(self.variables[expression.name], name=expression.name)
            case NegateExpression(): 
                value = self.emit_expression(expression.operand)
                return self.builder.sub(ir.Constant(value.type, 0), value)
            case NotExpression(): 
                value = self.emit_expression(expression.operand)
                return self.builder.xor(value, ir.Constant(self.i1, 1))
            case AssignmentExpression(): 
                name = expression.lvalue.name
                value = self.emit_expression(expression.rvalue)
                self.builder.store(value, self.variables[name])
                return value
            case BinaryExprExpression(): 
                left = self.emit_expression(expression.left)
                right = self.emit_expression(expression.right)
                op = expression.operator

                if op == TokenType.ADD:
                    return self.builder.add(left, right)
                if op == TokenType.SUB:
                    return self.builder.sub(left, right)
                if op == TokenType.MUL:
                    return self.builder.mul(left, right)
                if op == TokenType.DIV:
                    return self.builder.sdiv(left, right)
                if op == TokenType.MOD:
                    return self.builder.srem(left, right)

                if op == TokenType.AND:
                    return self.builder.and_(left, right)
                if op == TokenType.OR:
                    return self.builder.or_(left, right)

                predicates = {
                    TokenType.LESS_THAN: "<",
                    TokenType.LESS_THAN_OR_EQUAL_TO: "<=",
                    TokenType.GREATER_THAN: ">",
                    TokenType.GREATER_THAN_OR_EQUAL_TO: ">=",
                    TokenType.EQUAL_TO: "==",
                    TokenType.NOT_EQUAL_TO: "!=",
                }

                if op in predicates:
                    return self.builder.icmp_signed(
                        predicates[op], left, right
                    )

                raise ValueError(f"Unknown operator: {op}")

    def emit_statement(self, statement: Statement): 
        match statement: 
            case ModuleStatement(): 
                for statement in statement.code:
                    if self.builder.block.is_terminated:
                        break
                    self.emit_statement(statement)
            case BlockStatement(): 
                for statement in statement.code:
                    if self.builder.block.is_terminated:
                        break
                    self.emit_statement(statement)
            case IfStatement():
                condition = self.emit_expression(statement.condition)

                then_block = self.function.append_basic_block("if.then")
                end_block = self.function.append_basic_block("if.end")

                self.builder.cbranch(condition, then_block, end_block)

                self.builder.position_at_end(then_block)
                self.emit_statement(statement.statement)

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_block)

                self.builder.position_at_end(end_block)
            case IfElseStatement():
                condition = self.emit_expression(statement.condition)

                then_block = self.function.append_basic_block("if.then")
                else_block = self.function.append_basic_block("if.else")
                end_block = self.function.append_basic_block("if.end")

                self.builder.cbranch(condition, then_block, else_block)

                self.builder.position_at_end(then_block)
                self.emit_statement(statement.if_statement)

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_block)

                self.builder.position_at_end(else_block)
                self.emit_statement(statement.else_statement)

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_block)

                self.builder.position_at_end(end_block)
            case WhileStatement():
                cond_block = self.function.append_basic_block("while.cond")
                body_block = self.function.append_basic_block("while.body")
                end_block = self.function.append_basic_block("while.end")

                self.builder.branch(cond_block)

                self.builder.position_at_end(cond_block)
                condition = self.emit_expression(statement.condition)
                self.builder.cbranch(condition, body_block, end_block)

                self.loop_end_blocks.append(end_block)

                self.builder.position_at_end(body_block)
                self.emit_statement(statement.statement)

                if not self.builder.block.is_terminated:
                    self.builder.branch(cond_block)

                self.loop_end_blocks.pop()
                self.builder.position_at_end(end_block)
            case BreakStatement():
                if not self.loop_end_blocks:
                    raise ValueError("break outside loop")
                self.builder.branch(self.loop_end_blocks[-1])
            case IntVarDeclStatement():
                name = statement.name.value
                ptr = self.builder.alloca(self.i32, name=name)
                self.variables[name] = ptr
                self.builder.store(ir.Constant(self.i32, 0), ptr)
            case BoolVarDeclStatement():
                name = statement.name.value
                ptr = self.builder.alloca(self.i1, name=name)
                self.variables[name] = ptr
                self.builder.store(ir.Constant(self.i1, 0), ptr)
            case ExpressionStatement():
                self.emit_expression(statement.expression)
            case EOFStatement():
                raise ValueError("EOFStatement not supported")
    def finish(self):
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(self.i32, 0))

        return self.module

    def emit_assembly(self):
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        module = binding.parse_assembly(str(self.finish()))
        module.verify()

        target = binding.Target.from_default_triple()
        machine = target.create_target_machine(opt=0)

        return machine.emit_assembly(module)