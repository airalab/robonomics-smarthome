import sys
from utils import read_config, decrypt

text = str(sys.argv[1])
print(f"Got {text}")
config, ids = read_config('python_scripts/config.config')
seed = config['user'].seed_hex
decrypted = decrypt(seed, text)
print(decrypted)
