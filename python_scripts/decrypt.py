import sys
from utils import read_config, decrypt

text = str(sys.argv[1])
print(f"Got {text}")
keypair = read_config('python_scripts/config.config')
seed = keypair.seed_hex
decrypted = decrypt(seed, text)
print(decrypted)
