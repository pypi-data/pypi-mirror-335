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
            (r'masukkan "(.*?)" -> (\w+)', r'\2 = input("\1")'),
            (r'tampilkan "(.*?)"', r'print("\1")'),
            (r'tampilkan (.*?)\n', r'print(\1)\n'),
            (r'//.*', '')  # Hapus komentar
        ]
        
        for pattern, repl in replacements:
            code = re.sub(pattern, repl, code)
            
        # Hapus kurung kurawal
        code = code.replace('{', '').replace('}', '')
        
        return code