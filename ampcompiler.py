import sys
import ampyacc
import logging

output = ''


class AmpCompiler:
    def __init__(self,tree) -> None:
        self.tree = tree

    def compile(self):
        global output
        output += "import ampfunctions\n"

        self.walk_tree(self.tree)
        print(output)
    
    #walk through the nested list based using b-tree
    def walk_tree(self,tree):  
        if isinstance(tree,tuple):
            if isinstance(tree[0],tuple):
                self.walk_tree(tree[0]) #process the head
                self.walk_tree(tree[1]) #process the tail
            self.eval(tree)
                
    def str_val(self,tup):
        if tup[0]=='INT':
            return f"{tup[1]}"
        elif tup[0] == 'STR':
            return f"'{tup[1]}'"
        elif tup[0] == '@':
            return f"{tup[1]}"

    def flatten(self,test_tuple):
        
        if isinstance(test_tuple, tuple) and len(test_tuple) == 2 and not isinstance(test_tuple[0], tuple):
            res = [test_tuple]
            return tuple(res)
    
        res = []
        for sub in test_tuple:
            res += self.flatten(sub)
        return tuple(res)

    def eval(self, element):
        global output,flattened
        
        op = element[0]

        if op=='VAR':
            if isinstance(element[1],tuple):
                flattened = []
                flattened = self.flatten_list(element[1])
                for x in flattened:
                    if x != '@':
                        output += f"{x} = None\n"
            else:
                output += f"{element[2]} = None\n"
        elif op=='SET':
            output += f"{element[1]} = {self.str_val(element[2])}\n"
        elif op == 'IF':
            output += f"if {self.releval(element[1])}: \n"
            output += f"\t{self.eval(element[2])}"
        elif op == 'FUNC':
            return f"getattr(ampfunctions,'{element[1]}')(ampfunctions,{self.str_val(element[2])})\n"
        elif op == 'FOR':
            loopvar = element[1]
            initval = element[2]
            finval = element[4]
            stepval = element[5]
            nextval = element[6]
            direction = element[3]
            
            output += f"{loopvar} = {self.str_val(initval)}\n"
            output += f"while {loopvar} < {self.str_val(finval)}: \n"
            output += f"\t {self.eval(stepval)}"
            
            if direction == 'TO':
                output += f"\t {loopvar}+=1 \n"
            elif direction=='DOWNTO':
                output += f"\t {loopvar}-=1 \n"
        elif op == '@':
            output += f"{element[1]} = None\n"

    def flatten_list(self, nested_list):
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item)
            else:
                flattened.append(item)
        return flattened

    def releval(self, element):
        op = element[0]
        if op == 'GROUP':
            pass
        elif op == 'RELOP' or op == 'BINOP':
            return f"{self.str_val(element[2])} {element[1]} {self.str_val(element[3])} "
        