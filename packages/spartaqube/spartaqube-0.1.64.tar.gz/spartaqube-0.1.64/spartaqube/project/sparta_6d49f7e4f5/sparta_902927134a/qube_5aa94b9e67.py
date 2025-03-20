import ast
def sparta_e407c86c39(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_8363a03cbe(script_text):return sparta_e407c86c39(script_text)