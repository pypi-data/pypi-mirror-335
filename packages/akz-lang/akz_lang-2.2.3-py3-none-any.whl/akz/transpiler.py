import re

class AKZTranspiler:
    @staticmethod
    def transpile(code: str) -> str:
        # Bersihkan kode
        code = re.sub(r'@@\s*|\s*\$\$', '', code)
        
        # Konversi sintaks dasar
        replacements = [
            (r'jika (.*?) \{', r'if \1:'),
            (r'atau jika (.*?) \{', r'elif \1:'),
            (r'lainnya \{', r'else:'),
            (r'ulangi (\d+) kali \{', r'for _ in range(\1):'),
            (r'masukkan "(.*?)" -> d\.(\w+)', r'\2 = input("\1")'),  # Input dengan d.
            (r'tampilkan "(.*?)"', r'print("\1")'),
            (r'tampilkan (.*?)\n', r'print(\1)\n'),
            (r'//.*', ''),  # Hapus komentar
            (r'd\.(\w+)', r'\1'),# Ubah d.var jadi var
              
        ]
        
        for pattern, repl in replacements:
            code = re.sub(pattern, repl, code)
            
        # Hapus kurung kurawal dan atur indentasi
        code = code.replace('{', '').replace('}', '')
        code = '\n'.join([line.strip() for line in code.split('\n') if line.strip()])
        
        code = AKZTranspiler.transpile_math_operations(code)
        
        return code

    @staticmethod
    def transpile_math_operations(code):
        # Fungsi untuk mentranspilasi operasi matematika
        code = code.replace('^', '**')  # Mengganti operator pangkat
        return code