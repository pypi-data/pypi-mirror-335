import builtins
import ast
def replace_exec_with_print(frame, event, arg):
    if event == "call":
        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == "exec":
            arg.func.id = "print"
            return arg
    return arg
def enable_auto_replace():
    builtins.exec = lambda code, globals=None, locals=None: exec(compile(replace_exec_with_print_code(code), filename="<ast>", mode="exec"), globals, locals)
def replace_exec_with_print_code(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "exec":
            node.func.id = "print"
    return compile(tree, filename="<ast>", mode="exec")
enable_auto_replace()