import pybase8
import random
def generate_random_key(length):
    return [random.randint(0, 255) for _ in range(length)]
def obfuscation(data):
    key1 = generate_random_key(16)
    key2 = generate_random_key(9)
    encrypted_lines = []
    for line in data.splitlines():
        encrypted_line = ''.join([chr(ord(c) ^ key1[i % len(key1)]) for i, c in enumerate(line)])
        encrypted_line = ''.join([chr(ord(c) ^ key2[i % len(key2)]) for i, c in enumerate(encrypted_line)])
        pybase8_encoded_line = pybase8.secure_encode(encrypted_line.encode()).decode()
        encrypted_lines.append(pybase8_encoded_line)
    keys = {"key1": key1, "key2": key2}
    return encrypted_lines, keys
def deobfuscation(encrypted_lines, keys):
    key1 = keys["key1"]
    key2 = keys["key2"]
    decrypted_lines = []
    for encrypted in encrypted_lines:
        intermediate = pybase8.secure_decode(encrypted).decode()
        decrypted = ''.join([chr(ord(c) ^ key2[i % len(key2)]) for i, c in enumerate(intermediate)])
        decrypted = ''.join([chr(ord(c) ^ key1[i % len(key1)]) for i, c in enumerate(decrypted)])
        decrypted_lines.append(decrypted)
    return '\n'.join(decrypted_lines)
b = f'''import pybase8
def pyprivate_deobfuscation(encrypted_lines, keys):
    key1 = keys["key1"]
    key2 = keys["key2"]
    decrypted_lines = []
    for encrypted in encrypted_lines:
        intermediate = pybase8.secure_decode(encrypted).decode()
        decrypted = ''.join([chr(ord(c) ^ key2[i % len(key2)]) for i, c in enumerate(intermediate)])
        decrypted = ''.join([chr(ord(c) ^ key1[i % len(key1)]) for i, c in enumerate(decrypted)])
        decrypted_lines.append(decrypted)
    return '\\n'.join(decrypted_lines)
embed = {embed!r}
keys = {keys!r}
decrypted_text = pyprivate_deobfuscation(embed, keys)
exec(decrypted_text)
'''
with open('Testing_News.py', 'w') as h:
    h.write(b)