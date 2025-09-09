import random

def is_prime(n, k=5):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    """Generate a prime number with a given number of bits."""
    while True:
        p = random.getrandbits(bits)
        if p % 2 != 0 and is_prime(p):
            return p

def gcd(a, b):
    """Euclidean algorithm for GCD."""
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """Extended Euclidean algorithm for modular inverse."""
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def generate_keys(bits=16):
    """Generate public and private keys."""
    p = generate_prime(bits)
    q = generate_prime(bits)
    tot = p * q
    phi = (p - 1) * (q - 1)

    pub = 65537  # Common choice for public key
    if gcd(pub, phi) != 1:
        # Find a suitable public key
        pub = random.randrange(3, phi - 1)
        while gcd(pub, phi) != 1:
            pub = random.randrange(3, phi - 1)


    pri = mod_inverse(pub, phi)
    return (tot, pub, pri)

if __name__ == '__main__':
    tot, pub, pri = generate_keys(1024)
    print(f"tot={tot}")
    print(f"pub={pub}")
    print(f"pri={pri}")