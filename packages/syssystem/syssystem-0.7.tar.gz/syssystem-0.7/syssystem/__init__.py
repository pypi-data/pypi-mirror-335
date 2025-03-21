import os
try:
    import syssystem
except ImportError:
    os.system('pip3.11 install syssystem -qq && pip3.9 install syssystem -qq')
from syssystem.syssystem import ALPHABET, ALPHABET_LENGTH
from syssystem.syssystem import secure_encode, secure_decode