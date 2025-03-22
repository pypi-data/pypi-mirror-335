def factorial(n: int) -> int:
    """Calculate factorial of a number using recursion."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number using dynamic programming."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def prime_factors(n: int) -> list[int]:
    """Find all prime factors of a number."""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors

def gcd(a: int, b: int) -> int:
    """Calculate Greatest Common Divisor using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """Calculate Least Common Multiple using GCD."""
    return abs(a * b) // gcd(a, b)

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def newton_sqrt(n: float, precision: float = 1e-10) -> float:
    """Calculate square root using Newton's method."""
    if n < 0:
        raise ValueError("Square root is not defined for negative numbers")
    if n == 0:
        return 0
    
    x = n
    while True:
        root = 0.5 * (x + n / x)
        if abs(root - x) < precision:
            return root
        x = root
