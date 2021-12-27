import sys
from utils import read_config, encrypt

text = str(sys.argv[1])
print(f"Got {text}")
config, ids = read_config('python_scripts/config.config')
seed = config['user'].seed_hex
decrypted = encrypt(seed, text)
print(decrypted)