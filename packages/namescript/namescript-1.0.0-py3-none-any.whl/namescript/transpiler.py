import re
import argparse
from . import __version__

class NameScriptTranspiler:
    def __init__(self):
        self.replacements = [
            # BEGINNER SYNTAX
            # Variabel
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
            (r'^lainnya\s*\{', r'else:'),             # lainnya { → else:
            
            # Komentar
            (r'//(.*)$', r'#\1'),                     # // komentar → # komentar
            
            # String literal
            (r'"(.*?)"', r"'\1'"),                    # "teks" → 'teks'
            
            # DEEP SYNTAX
            # Fungsi
            (r'^fungsi\s+(\w+)\((.*?)\)\s*\{', r'def \1(\2):'),  # fungsi nama(param) { → def nama(param):
            (r'^kembalikan\s+(.*)$', r'return \1'),               # kembalikan nilai → return nilai
            
            # Perulangan
            (r'^ulangi\s+(\w+)\s+dalam\s+(\d+)\.\.(\d+)\s*\{', r'for \1 in range(\2, \3+1):'),  # ulangi i dalam 1..5 → for i in range(1, 6)
            (r'^ulangi\s+(\w+)\s+dalam\s+(.*?)\s*\{', r'for \1 in \2:'),                        # ulangi x dalam daftar → for x in daftar
            
            # Error handling
            (r'^coba\s*\{', r'try:'),                            # coba { → try:
            (r'^tangkap\s+sebagai\s+(\w+)\s*\{', r'except Exception as \1:'),  # tangkap sebagai err { → except Exception as err:
            (r'^tangkap\s*\{', r'except:'),                      # tangkap { → except:
            
            # Operasi logika
            (r'<dan>', r'and'),   # <dan> → and
            (r'<atau>', r'or'),   # <atau> → or
            (r'<tidak>', r'not'), # <tidak> → not
            
            # Struktur data
            (r'^daftar\((.*?)\)', r'list(\1)'),  # daftar(1,2,3) → list(1,2,3)
            (r'^kamus\((.*?)\)', r'dict(\1)'),   # kamus("a":1) → dict("a":1)
        ]
    
    def transpile(self, ns_code):
        python_code = []
        indent_level = 0
        
        for line in ns_code.split('\n'):
            line = line.strip()
            
            # Handle kurung kurawal tutup
            if '}' in line:
                indent_level = max(0, indent_level - 1)
                line = line.replace('}', '')
            
            # Proses semua pola regex
            for pattern, replacement in self.replacements:
                line = re.sub(pattern, replacement, line)
            
            # Tambahkan indentasi
            python_line = ' ' * (4 * indent_level) + line
            python_code.append(python_line)
            
            # Handle kurung kurawal buka
            if '{' in line:
                indent_level += 1
                line = line.replace('{', '')
        
        return '\n'.join(python_code)

def main():
    parser = argparse.ArgumentParser(
        prog='ns',
        description="NameScript Language Tools",
        epilog="Contoh penggunaan: ns ctp program.ns ke output.py"
    )
    
    subparsers = parser.add_subparsers(title="Perintah", dest="command")
    
    # Perintah: jalankan
    run_parser = subparsers.add_parser('jalankan', help='Jalankan file NS')
    run_parser.add_argument('file', help='File .ns yang akan dijalankan')
    run_parser.set_defaults(func=handle_jalankan)
    
    # Perintah: ctp
    ctp_parser = subparsers.add_parser('ctp', help='Konversi NS ke Python')
    ctp_parser.add_argument('input_file', help='File input .ns')
    ctp_parser.add_argument('ke', help='Kata penghubung (diabaikan)')
    ctp_parser.add_argument('output_file', help='File output .py')
    ctp_parser.set_defaults(func=handle_ctp)
    
    # Perintah: versi
    versi_parser = subparsers.add_parser('versi', help='Tampilkan versi')
    versi_parser.set_defaults(func=handle_versi)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def handle_jalankan(args):
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            ns_code = f.read()
        
        transpiler = NameScriptTranspiler()
        python_code = transpiler.transpile(ns_code)
        exec(python_code, {'__file__': args.file})
        
    except FileNotFoundError:
        print(f"Error: File {args.file} tidak ditemukan!")
    except Exception as e:
        print(f"Error saat eksekusi: {str(e)}")

def handle_ctp(args):
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            ns_code = f.read()
        
        transpiler = NameScriptTranspiler()
        python_code = transpiler.transpile(ns_code)
        
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"Berhasil dikonversi ke {args.output_file}")
        
    except FileNotFoundError:
        print(f"Error: File {args.input_file} tidak ditemukan!")
    except Exception as e:
        print(f"Error: {str(e)}")

def handle_versi(args):
    print(f"NameScript v{__version__}")

if __name__ == "__main__":
    main()