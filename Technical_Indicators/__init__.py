import os, re

listOfFiles = os.listdir('Technical_Indicators/')
pattern = ".py"

arr=list(filter(lambda x: pattern in x,listOfFiles))

arr.remove("__init__.py")


arr=list(map(lambda x: re.sub(pattern, '', x),arr))

__all__=arr