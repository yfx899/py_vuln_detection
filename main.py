import inspect
import ast

#Function you want to test
def foo(arg):

	a = user_input()
	eval(a)
	a = 1
	eval(a)
	a = user_input()
	def new_scope(arg):
		eval(a)

#user_input_method : which paramater it takes to taint this
tainted_methods = {'user_input': None}

tainted_variables = set()

#dang2 does not exist. For testing purposes
dangerous_methods = {'eval' : 0,
					'dang2': 0}

cleaning_methods = {'eval' : {'clean_eval'}}

#These functions do not exist. For testing purposes
all_cleaning_methods = {'clean_eval': 0,
						'false_clean_eval': 0}

variable_attributes = {'Name':'id',
'Dict':'',
'Num': 'n',
'Str':'s'
}

class VariableDef:
    def __init__(self, var_type, index, line_number, name):
        
        self.name = name
        self.var_type = var_type
        self.is_dangerous = False
        self.parameter_index = index
        self.pointer = None
        self.line_number = line_number

class SimpleVisitor(ast.NodeVisitor):
    def __init__(self, assumption):
        self.scope = [['global', {}]]
        self.classes = []
        #This handles functions that have not been found
        #And the assumption that it returns user input (or not)
        self.assume = assumption


    def visit_ClassDef(self, node, *args, **kwargs):
        #Class definition is technically not a new scope
        #But we will keep track of it anyway
        #To track class variables that may be used in features later on
        self.scope.append(['class', 1, node.name, {}])
        self.generic_visit(node)
        self.scope.pop()
    
    def visit_FunctionDef(self, node, *args, **kwargs):
        self.scope.append(['function', self.scope[-1][1] if (self.scope and self.scope[-1][1] == 'class') else None, node.name, {}])
        self.set_variables('function', node)
        self.generic_visit(node)

        self.scope.pop()
    #Todo
    def visit_Return(self, node, *args, **kwargs):
    	pass
    def visit_Global(self, node, *args, **kwargs):
        self.generic_visit(node)

    #To implement for  
    #For nested dangers
    #Imagine eval(func1(clean($var))
    def post_Order(node):
        pass

        #Assume everything returns user input
        #Unless we have found that it doesn't
    def dangerous_method_call(self, node, parent, level):
    	object_name = type(node).__name__
    	if object_name in  {'List', 'Name', 'Num', 'Str', 'Dict'}:
    		return self.is_dangerous(node)
    	if object_name == 'Call':
    		#We don't care about anymore dangerous calls
			#Under this, since it will be calleed recursively
			#Once generic visit hits again, anyways
			#So we are only looking for tainted functions or variables
    		if node.func.id in dangerous_methods:
    			if level:
	    			if self.dangerous_method_call(node.args[dangerous_methods[node.func.id]], node.func.id, 0):
	    				print('Potentially dangerous call at line number: ', node.lineno)
	    				return True
	    		return False
    		elif parent and (node.func.id in tainted_methods) and not level:
    			return True if tainted_methods[node.func.id] is None else self.dangerous_method_call(node.args[tainted_methods[node.func.id]], parent, level)
    		#Anything it returns will be cleaned for this function, so don't have to search past this
    		elif parent and (node.func.id in cleaning_methods[parent]):
    			return False
    		#If it's a cleaning function but it doesn't clean for this dangerous
    		#function, then assume it returns tainted user input if called with the input parameter
    		elif parent and (node.func.id in all_cleaning_methods):
    			return self.dangerous_method_call(node.args[all_cleaning_methods[node.func.id]], parent, level)
    		
    		#If we get here, it means we don't know what the function returns. We will return True if we assume it returns user input, or false.
    		#Potential for false positives. User can set this.
    		return self.assume



    def visit_Call(self, node, *args, **kwargs):
       self.dangerous_method_call(node, None, 1)
       self.generic_visit(node)
 

    def visit_Assign(self, node, *args, **kwargs):
        self.set_variables('regular', node)
        self.generic_visit(node)

    def decompose_variable_type_name(self, node):
        if hasattr(node, 'func'):
            return [node.func.id, 'function']
        if hasattr(node, 'id'):
            return [node.id, 'var']
        else:
            return [None, 'other']

        
        
    def is_dangerous(self, node):
        name, var_type = self.decompose_variable_type_name(node)
        if var_type in {'var', 'function'}:
            if name in tainted_variables: return True
            if name in tainted_methods: return True
            index = len(self.scope)-1
            while index >= 0:
                    if name in self.scope[index][-1]:
                        return self.scope[index][-1][name].is_dangerous
                    index -= 1
            return False






    #def is_dangerous(self, node, object_name):
    #	#Trace scope.
    #	if object_name == 'Name':
    #		return node.id in tainted_variables


    def set_variables(self, definition, node):
        if definition == 'function':
            for index, parameter in ((index, i.arg) for index, i in enumerate(node.args.args)):
                if parameter != 'self':
                    self.scope[-1][-1][parameter] = VariableDef('parameter', index, node.lineno, parameter)
        if definition == 'regular':
	        assignment_danger = self.is_dangerous(node.value)
	        for var_name in node.targets:
	        	new_var = VariableDef('regular', None, node.lineno, var_name.id)
	        	new_var.is_dangerous = assignment_danger
	        	self.scope[-1][-1][var_name.id] = new_var

		        	





simple_visitor = SimpleVisitor(True)
example_ast = ast.parse(inspect.getsource(foo))
simple_visitor.generic_visit(example_ast)
