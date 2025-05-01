import os
os.chdir(os.path.expanduser('~'))
print(os.getcwd())
print('hello from docker!')

with open('example.txt', 'w') as f:
    f.write('This is a line of text.')

print('hello from docker 1')
print('hello from docker 2')
print('hello from docker 3')
print('end')





