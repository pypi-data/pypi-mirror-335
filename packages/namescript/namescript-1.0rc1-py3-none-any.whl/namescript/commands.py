import argparse
from . import version
from .ctp import convert_to_python
from .transpiler import NameScriptTranspiler

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
    convert_to_python(args.input_file, args.output_file)

def handle_versi(args):
    print(f"NameScript v{version.__version__}")

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
    
    # Perintah: versi
    versi_parser = subparsers.add_parser('versi', help='Tampilkan versi')
    versi_parser.set_defaults(func=handle_versi)
    
    # Perintah: ctp
    ctp_parser = subparsers.add_parser('ctp', help='Konversi NS ke Python')
    ctp_parser.add_argument('input_file', help='File input .ns')
    ctp_parser.add_argument('ke', help='Kata penghubung (diabaikan)')
    ctp_parser.add_argument('output_file', help='File output .py')
    ctp_parser.set_defaults(func=handle_ctp)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()