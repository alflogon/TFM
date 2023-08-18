def rotate_left(x, n):
    return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF

def present_round(state, round_key):

    #       0    1     2    3    4    5    6    7    8    9    a    b    c    d    e    f

    SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2
    ]

    # Aplicar la operación XOR entre el estado actual y la clave de ronda
    state ^= round_key

    # Aplicar la capa de sustitución (S-Box)
    state = ((0x00000000000000FF & SBOX[state & 0xF]) |
             (0x000000000000FF00 & SBOX[(state >> 4) & 0xF]) |
             (0x0000000000FF0000 & SBOX[(state >> 8) & 0xF]) |
             (0x00000000FF000000 & SBOX[(state >> 12) & 0xF]) |
             (0x000000FF00000000 & SBOX[(state >> 16) & 0xF]) |
             (0x0000FF0000000000 & SBOX[(state >> 20) & 0xF]) |
             (0x00FF000000000000 & SBOX[(state >> 24) & 0xF]) |
             (0xFF00000000000000 & SBOX[(state >> 28) & 0xF]))

    # Aplicar la rotación hacia la izquierda de 4 bits
    state = rotate_left(state, 4)
    return state

def present_key_schedule(key):
    round_keys = [0] * 32

    # Convertir la clave de entrada en un número entero de 64 bits (80 bits con ceros de relleno)
    round_keys[0] = int(key, 16)

    # Generar las claves de ronda
    for i in range(1, 32):
        round_keys[i] = (round_keys[i - 1] << 61) | (round_keys[i - 1] >> 3)
        round_keys[i] = round_keys[i] & 0xFFFFFFFFFFFFFFFF
    return round_keys

def present_permutation(state):
    # Fase de permutación en el cifrado PRESENT

    state = ((state << 56) & 0xFF00000000000000) | ((state << 40) & 0x00FF000000000000) | \
            ((state << 24) & 0x0000FF0000000000) | ((state << 8) & 0x000000FF00000000) | \
            ((state >> 8) & 0x00000000FF000000) | ((state >> 24) & 0x0000000000FF0000) | \
            ((state >> 40) & 0x000000000000FF00) | ((state >> 56) & 0x00000000000000FF)
    return state

def present_encrypt(plain_text, key):

    # Convertir la clave a mayúsculas para validarla correctamente
    key = key.upper()

    # Validar que la clave tenga exactamente 16 caracteres hexadecimales
    while len(key) != 16 or not all(c in "0123456789ABCDEF" for c in key):
        print("Error: La clave debe tener exactamente 16 caracteres hexadecimales en total. Caracteres válidos: del 0 al 9 y desde la A la F")
        key = input("Introduce la clave (16 caracteres hexadecimales): ")

    # Aplicar relleno (padding) para asegurarnos de que el mensaje tenga un tamaño múltiplo de 16 bytes
    padded_text = plain_text + (16 - len(plain_text) % 16) * ' '

    # Generar las claves de ronda a partir de la clave de entrada
    round_keys = present_key_schedule(key)

    # Convertir el mensaje de entrada en un número entero de 64 bits (big-endian)
    state = int.from_bytes(padded_text.encode(), byteorder='big')

    # Aplicar 31 rondas de cifrado
    for i in range(31):
        state = present_round(state, round_keys[i])

    # Realizar la última operación XOR con la clave de ronda final
    cipher_text = state ^ round_keys[31]

    # Convertir el resultado cifrado en una cadena hexadecimal de 16 caracteres
    return hex(cipher_text)[2:].zfill(32).lstrip('0')

# Solicitar al usuario el mensaje y la clave
plain_text = input("Introduce el mensaje a cifrar: ")
key = input("Introduce la clave (16 caracteres hexadecimales): ")

cipher_text = present_encrypt(plain_text, key)
if cipher_text is not None:
    print("Texto cifrado:", cipher_text.upper())
