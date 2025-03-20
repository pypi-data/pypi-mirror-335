import random
import math

class EllipticCurve:
    """
    Represents an elliptic curve defined by the equation y^2 = x^3 + ax + b over a finite field of prime order p.

    Attributes:
        a (int): Coefficient 'a' of the curve equation.
        b (int): Coefficient 'b' of the curve equation.
        p (int): Prime modulus of the finite field.
        G (tuple): Base point G (Gx, Gy) on the curve.
        n (int): Order of the curve.
    """

    def __init__(self, a, b, p, Gx, Gy, n):
        """
        Initializes the elliptic curve with the given parameters.

        Args:
            a (int): Coefficient 'a' of the curve equation.
            b (int): Coefficient 'b' of the curve equation.
            p (int): Prime modulus of the finite field.
            Gx (int): x-coordinate of the base point G.
            Gy (int): y-coordinate of the base point G.
            n (int): Order of the curve.

        Raises:
            ValueError: If the base point G (Gx, Gy) does not lie on the curve.
        """
        self.a = a
        self.b = b
        self.p = p
        self.G = (Gx, Gy)
        self.n = n

        if not self.is_point_on_curve(self.G):
            raise ValueError("The base point G (Gx, Gy) does not lie on the curve.")

    def point_addition(self, P, Q):
        """
        Adds two points P and Q on the elliptic curve.

        Args:
            P (tuple): The first point (Px, Py) on the curve.
            Q (tuple): The second point (Qx, Qy) on the curve.

        Returns:
            tuple: The resulting point (Rx, Ry) after addition.
            None: If the points P and Q are inverses of each other.
        """
        if P is None:
            return Q
        if Q is None:
            return P
        if P == Q:
            if P[1] == 0:
                return None
            lam = (3 * P[0]**2 + self.a) * pow(2 * P[1], -1, self.p) % self.p
        else:
            if P[0] == Q[0]:
                return None
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, self.p) % self.p

        x_r = (lam**2 - P[0] - Q[0]) % self.p
        y_r = (lam * (P[0] - x_r) - P[1]) % self.p
        return (x_r, y_r)

    def scalar_multiplication(self, k, P):
        """
        Performs scalar multiplication of a point P by an integer k on the elliptic curve.

        Args:
            k (int): The scalar multiplier.
            P (tuple): The point (Px, Py) on the curve.

        Returns:
            tuple: The resulting point (Rx, Ry) after scalar multiplication.
            None: If the resulting point is the point at infinity.
        """
        result = None
        addend = P
        while k:
            if k & 1:
                result = self.point_addition(result, addend)
            addend = self.point_addition(addend, addend)
            k >>= 1
        return result

    def generate_private_key(self):
        """
        Generates a random private key.

        Returns:
            int: A randomly generated private key.
        """
        return random.getrandbits(256)

    def public_key_from_private(self, private_key):
        """
        Generates a public key from a given private key using scalar multiplication.

        Args:
            private_key (int): The private key.

        Returns:
            tuple: The corresponding public key (Px, Py).
        """
        return self.scalar_multiplication(private_key, self.G)

    def is_point_on_curve(self, P):
        """
        Checks if a given point P lies on the elliptic curve.

        Args:
            P (tuple): The point (Px, Py) to check.

        Returns:
            bool: True if the point lies on the curve, False otherwise.
        """
        if P is None:
            return False
        x, y = P
        return (y**2 - (x**3 + self.a * x + self.b)) % self.p == 0

    def print_curve(self):
        """
        Prints the equation of the elliptic curve.
        """
        print(f"Elliptic Curve: y^2 = x^3 + {self.a}x + {self.b} (mod {self.p})")

class KeyEntropyCalculator:
    """
    Calculates the entropy of keys for a given elliptic curve.

    Attributes:
        curve (EllipticCurve): The elliptic curve for which to calculate key entropy.
    """

    def __init__(self, curve):
        """
        Initializes the KeyEntropyCalculator with the given elliptic curve.

        Args:
            curve (EllipticCurve): The elliptic curve for which to calculate key entropy.
        """
        self.curve = curve

    def shannon_entropy(self, data):
        """
        Calculates the Shannon entropy of the given data.

        Args:
            data (list): The data for which to calculate entropy.

        Returns:
            float: The Shannon entropy of the data.
        """
        if not data:
            return 0
        entropy = 0
        byte_frequencies = {byte: data.count(byte) / len(data) for byte in set(data)}
        for freq in byte_frequencies.values():
            entropy -= freq * math.log2(freq)
        return entropy

    def private_key_to_byte_array(self, private_key):
        """
        Converts a private key to a byte array.

        Args:
            private_key (int): The private key to convert.

        Returns:
            list: The byte array representation of the private key.
        """
        return [int(x) for x in bin(private_key)[2:].zfill(256)]

    def generate_high_entropy_key(self, num_trials=100):
        """
        Generates a private key with high entropy by performing multiple trials.

        Args:
            num_trials (int): The number of trials to perform.

        Returns:
            tuple: The best private key and its entropy.
        """
        best_key = None
        max_entropy = 0
        for _ in range(num_trials):
            private_key = self.curve.generate_private_key()
            byte_array = self.private_key_to_byte_array(private_key)
            entropy = self.shannon_entropy(byte_array)
            if entropy > max_entropy:
                best_key = private_key
                max_entropy = entropy
        return best_key, max_entropy
    
def create_elliptic_curve_and_keys(num_trials=1000):
    """
    Creates an elliptic curve and generates keys with high entropy.

    Args:
        num_trials (int): The number of trials to perform for generating high entropy keys.

    Returns:
        dict: A dictionary containing the curve, best private key, public key, best entropy, and validity of the public key.
    """
    a = 56698187605326110043627228396178346077120614539475214109386828188763884139993
    b = 17577232497321838841075697789794520262950426058923084567046852300633325438902 
    p = 76884956397045344220809746629001649093037950200943055203735601445031516197751
    Gx = 63243729749562333355292243550312970334778175571054726587095381623627144114786
    Gy = 38218615093753523893122277964030810387585405539772602581557831887485717997975
    n = 0xA9FB57DBA1EEA9BC3E660A909D838D718AFCED59
    curve = EllipticCurve(a, b, p, Gx, Gy, n)
    curve.print_curve()
    entropy_calculator = KeyEntropyCalculator(curve)
    best_private_key, best_entropy = entropy_calculator.generate_high_entropy_key(num_trials)
    public_key = curve.public_key_from_private(best_private_key)

    print(f"Best Private Key: {best_private_key}")
    print(f"Highest Entropy: {best_entropy}")
    print(f"Public Key: {public_key}")
    print(f"Is Public Key Valid: {curve.is_point_on_curve(public_key)}")
    return {
        'curve': curve,
        'best_private_key': best_private_key,
        'public_key': public_key,
        'best_entropy': best_entropy,
        'is_public_key_valid': curve.is_point_on_curve(public_key)
    }
result = create_elliptic_curve_and_keys(num_trials=1000)