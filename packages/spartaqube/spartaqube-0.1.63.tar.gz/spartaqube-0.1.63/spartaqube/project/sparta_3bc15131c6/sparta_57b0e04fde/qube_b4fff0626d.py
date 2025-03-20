def sparta_0707544973(s):
	if isinstance(s,str):
		s=s.strip().lower()
		if s in['true','1','yes','y']:return True
		elif s in['false','0','no','n']:return False
	raise ValueError(f"Cannot convert '{s}' to a boolean.")
def sparta_5f9759fc60(assign_dict):
	A=assign_dict;C=A['guiType'];B=A['value']
	if C=='boolean':
		if not isinstance(B,bool):B=sparta_0707544973(B)
	D=f"import json\n{A['variableState']} = json.loads({A['interactiveVarDict']})";E=f"{A['variable']} = {B}";return{'assign_code':E,'assign_state_variable':D}