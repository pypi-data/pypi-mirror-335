import ast

with open('./test_code.py') as f:
    tree = ast.parse(f.read())

print(ast.dump(tree, indent=4))