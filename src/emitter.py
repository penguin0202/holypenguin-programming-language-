from TYPES.STATEMENT_TYPES import *
from TYPES.EXPRESSION_TYPES import *
from TYPES.TOKEN_TYPES import *
from llvmlite import ir, binding

class Emitter(): 
    def __init__(self): 
        self.module = ir.Module(name="main")
        self.module.triple = "x86_64-pc-windows-gnu"
        self.i32 = ir.IntType(32)
        self.i1 = ir.IntType(1)

        self.i8 = ir.IntType(8)
        self.i8p = self.i8.as_pointer()

        printf_type = ir.FunctionType(
            self.i32, [self.i8p], var_arg=True
        )
        scanf_type = ir.FunctionType(
            self.i32, [self.i8p], var_arg=True
        )
        getchar_type = ir.FunctionType(self.i32, [])
        
        self.getchar = ir.Function(self.module, getchar_type, name="getchar")
        self.printf = ir.Function(self.module, printf_type, name="printf")
        self.scanf = ir.Function(self.module, scanf_type, name="scanf")

        self.print_format = self.create_format_string(".print_fmt", "%d\n")
        self.input_format = self.create_format_string(".input_fmt", "%d")
        self.pause_format = self.create_format_string(
            ".pause_fmt", "Press Enter key to continue . . ."
        )

        self.variables = {}
        self.loop_end_blocks = []

        func_type = ir.FunctionType(self.i32, [])
        self.function = ir.Function(
            self.module, func_type, name="main"
        )

        entry = self.function.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)
    def create_format_string(self, name, text):
        string_type = ir.ArrayType(self.i8, len(text) + 1)

        string = ir.GlobalVariable(
            self.module, string_type, name=name
        )

        string.linkage = "private"
        string.global_constant = True
        string.initializer = ir.Constant(
            string_type,
            bytearray(text.encode("utf8") + b"\0")
        )

        return string
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
            case PrintStatement(): 
                value = self.emit_expression(statement.expression)

                fmt = self.builder.gep(
                    self.print_format,
                    [ir.Constant(self.i32, 0), ir.Constant(self.i32, 0)],
                    inbounds=True
                )

                self.builder.call(self.printf, [fmt, value])
            case InputStatement(): 
                variable_ptr = self.variables[statement.name.value]

                fmt = self.builder.gep(
                    self.input_format,
                    [ir.Constant(self.i32, 0), ir.Constant(self.i32, 0)],
                    inbounds=True
                )

                self.builder.call(self.scanf, [fmt, variable_ptr])

    def finish(self):
        if not self.builder.block.is_terminated:
            loop = self.function.append_basic_block("flush.loop")
            done = self.function.append_basic_block("flush.done")

            self.builder.branch(loop)
            self.builder.position_at_end(loop)

            char = self.builder.call(self.getchar, [])

            is_newline = self.builder.icmp_signed(
                "==", char, ir.Constant(self.i32, 10)
            )
            is_eof = self.builder.icmp_signed(
                "==", char, ir.Constant(self.i32, -1)
            )

            self.builder.cbranch(
                self.builder.or_(is_newline, is_eof),
                done,
                loop
            )

            self.builder.position_at_end(done)

            fmt = self.builder.gep(
                self.pause_format,
                [ir.Constant(self.i32, 0), ir.Constant(self.i32, 0)],
                inbounds=True
            )

            self.builder.call(self.printf, [fmt])
            self.builder.call(self.getchar, [])

            self.builder.ret(ir.Constant(self.i32, 0))

        return self.module

    def emit_assembly(self):
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        module = binding.parse_assembly(str(self.finish()))
        module.verify()

        target = binding.Target.from_triple("x86_64-pc-windows-gnu")
        target_machine = target.create_target_machine(opt=0, codemodel="default")

        module.data_layout = str(target_machine.target_data)

        print(target_machine.triple)

        return target_machine.emit_assembly(module)