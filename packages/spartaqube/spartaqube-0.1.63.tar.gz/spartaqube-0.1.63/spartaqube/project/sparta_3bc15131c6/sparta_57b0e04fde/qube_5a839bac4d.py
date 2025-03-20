import ast
def sparta_f779800c1e(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_c99e2a0b36(script_text):return sparta_f779800c1e(script_text)