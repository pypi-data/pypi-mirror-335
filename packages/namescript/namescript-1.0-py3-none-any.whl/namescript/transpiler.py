import re

class NameScriptTranspiler:
    def __init__(self):
        self.replacements = [
            (r'^d\s+(\w+)\s*=\s*(.*)$', r'\1 = \2'),  # d x = 5 → x = 5
            (r'<d_(\w+)>', r'\1'),                     # <d_x> → x
            
            # I/O
            (r'tampilkan\s+(.*)$', r'print(\1)'),      # tampilkan → print
            (r'masukan\((.*?)\)', r'input(\1)'),       # masukan → input
            
            # Operator matematika
            (r'<t>', r'+'),   # tambah
            (r'<k>', r'-'),   # kurang
            (r'<a>', r'*'),   # kali
            (r'<b>', r'/'),   # bagi
            
            # Percabangan
            (r'^jika\s+(.*?)\s*\{', r'if \1:'),        # jika kondisi { → if kondisi:
            (r'^lainnya\s*\{', r'else:'),              # lainnya { → else:
            
            # Komentar
            (r'//(.*)$', r'#\1'),                     # komentar → # komentar
            
            # String literal
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