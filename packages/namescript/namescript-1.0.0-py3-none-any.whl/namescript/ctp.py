from .transpiler import NameScriptTranspiler

def convert_to_python(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            ns_code = f.read()
        
        transpiler = NameScriptTranspiler()
        python_code = transpiler.transpile(ns_code)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"Berhasil dikonversi ke {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File {input_file} tidak ditemukan!")
    except Exception as e:
        print(f"Error: {str(e)}")