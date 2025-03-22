import os
import argparse
from . import version
from .ctp import convert_to_python
from .transpiler import NameScriptTranspiler

def validate_ns_file(value):
    if not value.endswith('.ns'):
        raise argparse.ArgumentTypeError("File input harus berekstensi .ns")
    return value

def validate_py_file(value):
    if not value.endswith('.py'):
        raise argparse.ArgumentTypeError("File output harus berekstensi .py")
    return value

def handle_jalankan(args):
    try:
        # Validasi ekstensi otomatis oleh argparse
        with open(args.file, 'r', encoding='utf-8') as f:
            ns_code = f.read()
        
        transpiler = NameScriptTranspiler()
        python_code = transpiler.transpile(ns_code)
        exec(python_code, {'__file__': args.file})
        
    except Exception as e:
        print(f"Error: {str(e)}")

def handle_ctp(args):
    # Validasi otomatis oleh argparse
    convert_to_python(args.input_file, args.output_file)

def handle_versi(args):
    print(f"NameScript v{version.__version__}")

def main():
    parser = argparse.ArgumentParser(
        prog='ns',
        description="NameScript Language Tools",
        epilog="Contoh:\n  ns jalankan program.ns\n  ns ctp program.ns ke output.py"
    )
    
    subparsers = parser.add_subparsers(title="Perintah", dest="command")
    
    # Perintah: jalankan
    run_parser = subparsers.add_parser('jalankan', help='Jalankan file .ns')
    run_parser.add_argument(
        'file', 
        type=validate_ns_file,
        help='File input (.ns)'
    )
    run_parser.set_defaults(func=handle_jalankan)
    
    # Perintah: ctp
    ctp_parser = subparsers.add_parser(
        'ctp', 
        help='Konversi .ns ke .py',
        formatter_class=argparse.RawTextHelpFormatter
    )
    ctp_parser.add_argument(
        'input_file',
        type=validate_ns_file,
        help='File input (.ns)'
    )
    ctp_parser.add_argument(
        'ke',
        help='Kata penghubung (harus "ke")',
        metavar='ke'
    )
    ctp_parser.add_argument(
        'output_file',
        type=validate_py_file,
        help='File output (.py)'
    )
    ctp_parser.set_defaults(func=handle_ctp)
    
    # Perintah: versi
    versi_parser = subparsers.add_parser('versi', help='Tampilkan versi')
    versi_parser.set_defaults(func=handle_versi)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()