#!/usr/bin/env python
# coding: utf-8


import sys, json

for file in sys.argv[1:]:
    print('#!/usr/bin/env python')
    print('# coding: utf-8')

    code = json.load(open(file))
    
    for cell in code['cells']:
        if cell['cell_type'] == 'code':
            for line in cell['source']:
                print(line, end='')
            print('\n')
        elif cell['cell_type'] == 'markdown':
            for line in cell['source']:
                print('#', line, end = '')
            print('\n')

