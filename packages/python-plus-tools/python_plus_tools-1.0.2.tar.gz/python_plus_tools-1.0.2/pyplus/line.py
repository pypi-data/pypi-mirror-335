from .tools import operators

variables = {}

class LineCode:
    "Linecode main."
    index = 0

    def __hash__(self):
        LineCode.index+= 1
        return LineCode.index

    def do(self):
        ...

    def __str__(self):
        return "<class Linecode from line.lineCodeMain>"

class SetV(LineCode):
    "Set Variable"
    def __init__(self,name:str,value):
        assert isinstance(name,str)
        self.name = name
        self.value = value
    
    def do(self):
        variables[self.name] = self.value
    
    def __str__(self):
        return "<function SetV from line.lineCodeMain>"

class GetV(LineCode):
    "Get the variable."
    def __init__(self,name:str):
        assert isinstance(name,str)
        self.name = name
    
    def do(self):
        return variables[self.name]
    
    def __str__(self):
        return "<function GetV from line.lineCodeMain>"

class ChangeV(LineCode):
    "Change the variable."
    def __init__(self,name:str,dv,op):
        self.name = name
        self.dv = dv
        self.op = op
    
    def do(self):
        variables[self.name] = self.op(variables[self.name],self.dv)
    
    def __str__(self):
        return "<function ChangeV from line.lineCodeMain>"

class Op(LineCode):
    "Operator."
    def __init__(self,left,op,value):
        self.left = left
        self.op = op
        self.value = value

    def do(self):
        if isinstance(self.left,str):
            return self.op(variables[self.left],self.value)
        elif isinstance(self.left,LineCode):
            return self.op(self.left.do(),self.value)
        else:
            return self.op(self.left,self.value)
        
    def __str__(self):
        return "<function Op from line.lineCodeMain>"
        
class If(LineCode):
    def __init__(self,*args,**kwargs):
        from typing import Set
        if len(args) == 4:
            self.condition = args[0]
            self.doCode:Set[LineCode] = args[1]
            self.elseDo:Set[LineCode] = args[3]
        elif len(args) == 2:
            self.condition = args[0]
            self.doCode:Set[LineCode] = args[1]
            self.elseDo:Set[LineCode] = set()

    def do(self):
        if self.condition.do():
            for code in self.doCode:
                code.do()
        elif self.elseDo:
            for code in self.elseDo:
                code.do()
    
    def __str__(self):
        return "<function If from line.lineCodeMain>"
    
class For(LineCode):
    def __init__(self,initContent,judgeContent,loopContent,loopCode):
        self.initContent = initContent
        self.judgeContent = judgeContent
        self.loopContent = loopContent
        self.loopCode = loopCode
    
    def do(self):
        self.initContent.do()
        while self.judgeContent.do():
            for code in self.loopCode:
                code.do()
            self.loopContent.do()

    def __str__(self):
        return "<function For from line.lineCodeMain>"
    
class Print(LineCode):
    def __init__(self,string):
        self.string = string
    
    def do(self):
        if isinstance(self.string,str):
            print(self.string)
        elif isinstance(self.string,LineCode):
            print(self.string.do())

class NameSpace:
    def __init__(self,*args):
        self.arr = args
    
    def run(self):
        for code in self.arr:
            code.do()

def run(*code):
    """run the line code."""
    NameSpace(*code).run()
