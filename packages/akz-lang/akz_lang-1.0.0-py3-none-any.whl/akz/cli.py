import argparse
import sys
from .transpiler import AKZTranspiler

def main():
    parser = argparse.ArgumentParser(
        description='AKZ Language v1.0.0',
        usage='''akz <command> [args]
        
Commands:
  run      Jalankan file .akz langsung
  compile  Compile ke file Python
'''
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Run Command
    run_parser = subparsers.add_parser('run', help='Jalankan file .akz')
    run_parser.add_argument('file', help='File .akz yang akan dijalankan')
    
    # Compile Command
    compile_parser = subparsers.add_parser('compile', help='Compile ke Python')
    compile_parser.add_argument('input', help='File input .akz')
    compile_parser.add_argument('-o', '--output', help='File output .py')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        try:
            with open(args.file, 'r') as f:
                akz_code = f.read()
            py_code = AKZTranspiler.transpile(akz_code)
            exec(py_code)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' tidak ditemukan!")
            sys.exit(1)
            
    elif args.command == 'compile':
        try:
            with open(args.input, 'r') as f:
                akz_code = f.read()
            py_code = AKZTranspiler.transpile(akz_code)
            output_file = args.output or 'output.py'
            with open(output_file, 'w') as f:
                f.write(py_code)
            print(f"Berhasil membuat {output_file}!")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
            
    else:
        parser.print_help()