import sys
import os
# Garantir que o diretório do workspace esteja no sys.path para que 'src' seja importável durante testes
root = os.path.dirname(__file__)
if root not in sys.path:
    sys.path.insert(0, root)
