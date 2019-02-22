import inspect
import ast

#Your test class/function
class Test:
    def __init__(self):
        self.bar = input()
    def foo(self):
        eval(self.bar)
        b = raw_input()
        def find():
            bar = 'change'
            eval(self.bar)
            eval(b)

            
#Methods, variables, etc
user_inputs = {'raw_input', 'input'}
#Function name, dangerous parameter, cleaning functions
bad_functions = {

    'eval' : [0, []]

              }

results = set()



class VariableDef:
    def __init__(self, var_type, index, line_number, name):
        
        self.name = name
        #type (parameter/local/nonlocal/global/instance/class (self)/regular)
        self.var_type = var_type
        self.is_dangerous = False
        #refers to parameter variables only
        self.parameter_index = index
        self.pointer = None
        self.line_number = line_number
        
        
class SimpleVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scope = [['global', {}]]


    def visit_ClassDef(self, node, *args, **kwargs):
        #Class definition is technically not a new scope
        #But we will keep track of it anyway
        #To track class variables that may be used in features later on
        self.scope.append(['class', node.name, {}])
        self.generic_visit(node)
        self.scope.pop()
    
    def visit_FunctionDef(self, node, *args, **kwargs):
        self.scope.append(['function', node.name, {}])
        self.set_variables('function', node)
        self.generic_visit(node)
        self.scope.pop()
    #Todo
    def visit_Global(self, node, *args, **kwargs):
        self.generic_visit(node)

    #To implement for  
    #For nested dangers
    #Imagine eval(func1(clean($var))
    def post_Order(node):
        pass

    def visit_Call(self, node, *args, **kwargs):
        
        if hasattr(node, 'args'):
            if node.func.id in bad_functions and len(node.args) > bad_functions[node.func.id][0]:
                index = bad_functions[node.func.id][0]
                if hasattr(node.args[index], 'func'):
                    if node.args[index].func.id in user_inputs:
                        results.add((node.func.id, node.lineno))
                else:
                    var_name, var_type = self.find_type(node.args[index])

                    #This may be confusing, but what it means is that if its a regular or "class variable" without self.
                    #As, you can onyl refer to class/instance variables by including a self.
                    #Then resolve the scope as usual. Otherwise, if it's a self which explicity
                    #tells you to find the "class/instance" variable, then restrict it to class
                    #Should change this
                    
                    scope = 'regular' if var_type == 'regular' or var_type == 'class' else 'class'
                    result = self.is_dangerous(var_name, scope)
                    if var_name in user_inputs or result:
                        if result.var_type == 'parameter':
                            #User defined dangerous function
                            bad_functions[node.func.id] = [result.parameter_index, []]
                        results.add((node.func.id, node.lineno, result))

            
        self.generic_visit(node)

    def visit_Assign(self, node, *args, **kwargs):
        self.set_variables('regular', node)
        self.generic_visit(node)




    #Is the declaration a variable or function or...
    #Takes assign object that has a value attribute
    def declaration_type(self, node):
        if hasattr(node.value, 'func'):
            return [node.value, node.value.func.id, 'function']
        if hasattr(node.value, 'id'):
            return [node.value, node.value.id, 'var']
        else:
            return [node.value, None, 'other']
        
 
    def is_dangerous(self, var, scope):
        index = len(self.scope)-1
        while index > 0:
            if scope == 'class' and self.scope[index][0] == 'class':
                 if var in self.scope[index][-1]:
                     if self.scope[index][-1][var].is_dangerous:
                         return self.scope[index][-1][var]
                 return False

            if scope == 'class' and var in self.scope[index][-1] and self.scope[index][var].var_type == 'self':
                if self.scope[index][var].is_dangerous:
                    return self.scope[index][var]
                else:
                    return False
                
            if scope == 'regular' and var in self.scope[index][-1] and self.scope[index][0] != 'class':
                if self.scope[index][-1][var].is_dangerous:
                    return self.scope[index][-1][var]
                else:
                    return False
            index -= 1
        return False

    def find_class(self):
        index = len(self.scope)-1
        while index > 0:
            if self.scope[index][0] == 'class':
                return self.scope[index]
            index -= 1

        
    #The type of variable
    #Takes name object
    def find_type(self, node):
        if type(node).__name__ == 'Attribute':
            if node.value.id == 'self':
                return [node.attr, 'self']
        if self.scope and self.scope[-1][0] == 'class':
            return [node.id, 'class']
        return [node.id, 'regular']

    def set_variables(self, definition, node):
        if definition == 'function':
            for index, parameter in ((index, i.arg) for index, i in enumerate(node.args.args)):
                if parameter != 'self':
                    self.scope[-1][-1][parameter] = VariableDef('parameter', index, node.lineno, parameter)
        
        if definition == 'regular':
            assignment_node, assignment_name, assignment_type = self.declaration_type(node)
            if assignment_type == 'var' and self.find_type(assignment_node)[-1] == 'regular':
                scope = 'regular'
            else:
                scope = 'class'
                
            class_ = self.find_class()
            assignment_danger = self.is_dangerous(assignment_name, scope)
            for var_name, var_type in (self.find_type(target) for target in node.targets):
  
                new_var = VariableDef('regular', None, node.lineno, var_name)
                if assignment_name in user_inputs or assignment_danger:
                    new_var.is_dangerous = True
                    if not assignment_danger:
                        new_var.pointer = assignment_name
                    else:
                        new_var.pointer = assignment_danger
                    if var_type == 'self':
                        new_var.var_type = 'self'
                        if var_name in class_:
                            class_[-1][var_name] = new_var
                        else:
                            self.scope[-1][-1][var_name] = new_var
                    else:
                        self.scope[-1][-1][var_name] = new_var
                        
                elif var_type == 'self' and var_name in class_:
                    if class_[-1][var_name].is_dangerous:
                        class_[-1][var_name].is_dangerous = False
                            
                elif var_name in self.scope[-1][-1] and self.scope[-1][-1][var_name].is_dangerous:
                    self.scope[-1][-1][var_name] = new_var
                #Move everything initialized in __init__ so it will  still show up when the __init__ scope pops
                if self.scope and self.scope[-1][1] == '__init__':
                    for var in self.scope[-1][-1]:
                        class_[-1][var] = self.scope[-1][-1][var]
        


    


simple_visitor = SimpleVisitor()
example_ast = ast.parse(inspect.getsource(Test))
simple_visitor.generic_visit(example_ast)

all_paths = []
for vuln in results:
    path = []
    path.append('Line Number ' + str(vuln[1]))
    path.append(' ---> ' + vuln[0] + ', ')
    if len(vuln) > 2:
        temp = vuln[2]
        while type(temp) != str:
            path.append('Line Number ' + str(temp.line_number))
            path.append(' ---> ' + temp.name + ', ')
            temp = temp.pointer
        path.append(' ---> ' + temp)
        
    all_paths.append(''.join(path))

for path in all_paths:
    print(path)


