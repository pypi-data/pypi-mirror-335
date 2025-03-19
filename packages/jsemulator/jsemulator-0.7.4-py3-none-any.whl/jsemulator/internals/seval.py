import jsparser
from .space import Space
from . import fill_space
from .byte_trans import ByteCodeGenerator
from .code import Code
from .simplex import *


jsparser.parser.ENABLE_jsemulator_ERRORS = lambda msg: MakeError(u'SyntaxError', unicode(msg))

def get_js_bytecode(js):
    a = ByteCodeGenerator(Code())
    d = jsparser.parse(js)
    a.emit(d)
    return  a.exe.tape
    
def eval_js_vm(js, debug=False):
    a = ByteCodeGenerator(Code(debug_mode=debug))
    s = Space()
    a.exe.space = s
    s.exe = a.exe

    d = jsparser.parse(js)

    a.emit(d)
    fill_space.fill_space(s, a)
    if debug:
        from pprint import pprint
        pprint(a.exe.tape)
        print()
    a.exe.compile()

    return a.exe.run(a.exe.space.GlobalObj)
