import math
import numpy as np
from typing import Tuple, Union

# Type alias for inputs that can be float or numpy array
NumericType = Union[float, np.ndarray]
#Bandi's first commit/comment

class BasicKLJNModel:
    """
    A basic model of the Kirchhoff-Law-Johnson-Noise (KLJN) secure key exchange system.
    This model calculates the voltages and current in the KLJN circuit based on given parameters.
    """

    def __init__(self, r_h: float, r_l: float, r_w: float):
        """
        Initialize the KLJN model with resistance values.

        Args:
            r_h (float): Value of the high resistance in ohms.
            r_l (float): Value of the low resistance in ohms.
            r_w (float): Value of the wire resistance in ohms.
        """
        self.r_h = r_h
        self.r_l = r_l
        self.r_w = r_w

    def calculate_generator_sd(self, bit: bool, default_sd: float) -> float:
        """
        Calculate the standard deviation of the noise generator based on the bit value.

        Args:
            bit (bool): True for high resistance, False for low resistance.
            default_sd (float): Default standard deviation of the noise generator.

        Returns:
            float: Standard deviation of the noise generator.
        """
        if bit:
            return default_sd
        else:
            return default_sd / math.sqrt(self.r_h) * math.sqrt(self.r_l)

    def calculate_circuit_values(self, gen_1: NumericType, gen_2: NumericType, r_1: NumericType, r_2: NumericType) \
            -> Tuple[NumericType, NumericType, NumericType]:
        """
        Calculate the voltages and current in the KLJN circuit.

        Args:
            gen_1 (float): Voltage of the first noise generator.
            gen_2 (float): Voltage of the second noise generator.
            r_1 (float): Resistance at the first end (either r_h or r_l).
            r_2 (float): Resistance at the second end (either r_h or r_l).

        Returns:
            Tuple[float, float, float]: Voltage at end 1, Voltage at end 2, Current in the loop.
        """
        i_loop = (gen_1 - gen_2) / (r_1 + r_2 + self.r_w)
        u1 = gen_1 - i_loop * r_1
        u2 = gen_2 + i_loop * r_2
        return u1, u2, i_loop

