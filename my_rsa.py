from sympy import randprime
def generate_keypair(p,q):
    while p==q:
        q=randprime(100, 1000)
    n = p*q
    phi = (p-1)*(q-1)

    e=65537
    d= inverse_mod(e, phi)

    return (e,n), (d,n)


def gcd(a, b):
    """Find gcd(a, b)"""
    while b!= 0:
        a, b = b, a%b
    return a

def inverse_mod(a, p):
    """Find inverse coeffiecient by mod p"""
    if p == 1:
        return 0

    r0, r1 = a, p
    s0, s1 = 1, 0

    while r1 > 0:
        q = r0//r1
        r0, r1 = r1, r0-(q*r1)
        s0, s1 = s1, s0-(q*s1)

    if r0 != 1:
        raise ValueError("gcd(a, p) is not equal 1")
    if s0 < 0:
        s0+=p

    return s0

def encrypt(public_key, plaintext):
    """Encrypt plain text"""
    e, n = public_key
    ciphertext=[]
    for char in plaintext:
        m= ord(char)
        c= pow(m, e, n)
        ciphertext.append(c)
    return ciphertext

def decrypt(private_key, ciphertext):
    """Decrypt encoded text"""
    d, n = private_key
    plaintext_chars = []
    for c in ciphertext:
        m= pow(c, d, n)
        char=chr(m)
        plaintext_chars.append(char)

    return "".join(plaintext_chars)
