import re

class GCodeLine:
    """
    Representa uma única linha de comando GCode, já traduzida para Python.
    """
    def __init__(self, original_line):
        self.original = original_line
        self.command = None  # Ex: ('G', 1) para G01
        self.params = {}     # Ex: {'X': -2.0, 'Z': -10.0, 'F': 150.0}
        self.comment = ""
        self._parse()

    def _parse(self):
        line = self.original.strip()
        
        # 1. Separar as fofocas (Comentários com ;)
        if ';' in line:
            line, self.comment = line.split(';', 1)
            self.comment = self.comment.strip()
            
        # Remove também comentários com parênteses ex: (passe final)
        line = re.sub(r'\(.*?\)', '', line).strip()
        
        if not line:
            return  # Era só uma linha vazia ou só comentário
            
        # 2. A Mágica: Achar todos os pares de Letra + Número
        # Padrão: Uma letra, opcionalmente espaços, e um número (com ou sem ponto/menos)
        tokens = re.findall(r'([A-Z])\s*(-?\d*\.?\d+)', line.upper())
        
        if not tokens:
            return
            
        # 3. O primeiro token geralmente é o comando mestre (G ou M)
        cmd_letter, cmd_val = tokens[0]
        # Converte para int se não tiver ponto decimal, senao float
        cmd_number = float(cmd_val) if '.' in cmd_val else int(cmd_val)
        self.command = (cmd_letter, cmd_number)
        
        # 4. O restante são os parâmetros (X, Z, F, R, etc)
        for letter, val in tokens[1:]:
            self.params[letter] = float(val)
            
    def __repr__(self):
        return f"<Comando={self.command[0]}{self.command[1]} Params={self.params}>"

def parse_gcode(gcode_text):
    """Lê um bloco de texto inteiro GCode e devolve uma lista de comandos traduzidos."""
    parsed_lines = []
    for line in gcode_text.splitlines():
        parsed = GCodeLine(line)
        if parsed.command: # Só adiciona se tiver comando válido
            parsed_lines.append(parsed)
    return parsed_lines

# =====================================================================
# ÁREA DE TESTE
# =====================================================================
if __name__ == "__main__":
    codigo_teste = """
    G00 X0 Z0 ; Ir para o inicio rapidao
    G01 X-2.5 Z-10.0 F150 (corte rapido e profundo)
    G76 P1.5 Z-30 X-1.0 D0.3 K0.5 ; Ciclo de rosca M10
    M05 ; Para fuso
    """
    
    print("--- Traduzindo o GCode para o Cérebro do Raspberry ---")
    comandos = parse_gcode(codigo_teste)
    
    for cmd in comandos:
        print(f"Letra Mestra: {cmd.command[0]} | Número: {cmd.command[1]:02} | Argumentos: {cmd.params}")
