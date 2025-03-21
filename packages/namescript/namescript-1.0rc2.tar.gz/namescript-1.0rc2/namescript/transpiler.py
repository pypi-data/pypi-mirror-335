import re

class NameScriptTranspiler:
    def __init__(self):
        self.replacements = [
            (r'^d\s+(\w+)\s*=\s*(.*)$', r'\1 = \2'),
            (r'<d-(\w+)>', r'\1'),
            (r'<t>', r'+'),
            (r'<k>', r'-'),
            (r'<a>', r'*'),
            (r'<b>', r'/'),
            (r'masukan\((.*?)\)', r'input(\1)'),
            (r'^tampilkan\s+(.*)$', r'print(\1)'),
            (r'//(.*)$', r'#\1'),
            (r'"(.*?)"', r"'\1'")
        ]
    
    def transpile(self, ns_code):
        python_code = []
        indent_level = 0
        
        for line in ns_code.split('\n'):
            line = line.strip()
            
            if '}' in line:
                indent_level = max(0, indent_level - 1)
                line = line.replace('}', '')
            
            for pattern, replacement in self.replacements:
                line = re.sub(pattern, replacement, line)
            
            python_line = ' ' * (4 * indent_level) + line
            python_code.append(python_line)
            
            if '{' in line:
                indent_level += 1
                line = line.replace('{', '')
        
        return '\n'.join(python_code)