import math
from decimal import Decimal, getcontext, DecimalTuple
from functools import reduce
from operator import mul
from random import normalvariate

Variability = Decimal


# Pi with 500 significant digits
# pi: Decimal = Decimal("3.14159265358979323846264338327950288419716939937510
#                          58209749445923078164062862089986280348253421170679
#                          82148086513282306647093844609550582231725359408128
#                          48111745028410270193852110555964462294895493038196
#                          44288109756659334461284756482337867831652712019091
#                          45648566923460348610454326648213393607260249141273
#                          72458700660631558817488152092096282925409171536436
#                          78925903600113305305488204665213841469519415116094
#                          33057270365759591953092186117381932611793105118548
#                          07446237996274956735188575272489122793818301194912")

# Pi based on math float value for compatibility without requiring import of pi from here
PI: Decimal = Decimal(math.pi)
TAU: Decimal = Decimal(2 * math.pi)


# TODO: calculate pi for Decimal with series
#
# def calculate_pi(precision):
#     """
#     Calculates pi using the Chudnovsky algorithm.
#
#     Args:
#         precision (int): The desired number of decimal places for the result.
#
#     Returns:
#         Decimal: The value of pi calculated to the specified precision.
#     """
#     getcontext().prec = precision + 1  # Set the precision for Decimal calculations
#
#     k = 0
#     pi = Decimal(0)
#     while k < precision:
#         pi += (Decimal(-1) ** k * Decimal(factorial(6 * k)) * (13591409 + 545140134 * k)) / (
#                     Decimal(factorial(3 * k)) * Decimal(factorial(k)) ** 3 * Decimal(640320) ** (3 * k + 1.5))
#         k += 1
#     pi = pi * Decimal(12) / (Decimal(640320) ** Decimal(3 / 2))
#
#     return pi.quantize(Decimal(str(10 ** -precision)))


def leading_decimal_zeroes(value: Decimal) -> int:
    value_tuple: DecimalTuple = value.as_tuple()
    counter: int = -1 * (len(value_tuple.digits) + value_tuple.exponent)
    return counter


def factorial(value: Decimal) -> Decimal:
    factorial_: Decimal = Decimal(math.factorial(int(value)))
    return factorial_


def sin(angle: Decimal) -> Decimal:
    """
    Calculate the sine of a Decimal value using power series expansion.
    """
    decimal_digits_precision: int = getcontext().prec

    sin_value: Decimal = Decimal(0)

    angle: Decimal = angle % TAU
    sign: Decimal = Decimal(1)
    power: Decimal = Decimal(1)

    while True:
        value: Decimal = angle ** power
        factorial_: Decimal = factorial(value=power)
        term: Decimal = value / factorial_

        if leading_decimal_zeroes(term) > decimal_digits_precision:
            break

        sin_value += sign * term
        sign *= Decimal(-1)
        power += Decimal(2)
    return sin_value


def cos(angle: Decimal) -> Decimal:
    """
    Calculate the cosine of a Decimal value using power series expansion.
    """
    decimal_digits_precision: int = getcontext().prec

    cos_value: Decimal = Decimal(1)

    angle: Decimal = angle % TAU
    sign: Decimal = Decimal(-1)
    power: Decimal = Decimal(2)

    while True:
        value: Decimal = angle ** power
        factorial_: Decimal = factorial(value=power)
        term: Decimal = value / factorial_

        if leading_decimal_zeroes(term) > decimal_digits_precision:
            break

        cos_value += sign * term
        sign *= Decimal(-1)
        power += Decimal(2)
    return cos_value


def sin_cos(angle: Decimal) -> tuple[Decimal, Decimal]:
    """
    Calculate the sine and cosine values using power series expansion.
    """
    decimal_digits_precision: int = getcontext().prec

    sin_value: Decimal = Decimal(0)
    cos_value: Decimal = Decimal(1)

    angle: Decimal = angle % TAU
    sin_sign: Decimal = Decimal(1)
    sin_power: Decimal = Decimal(1)
    cos_sign: Decimal = Decimal(-1)
    cos_power: Decimal = Decimal(2)

    while True:
        sin_angle_power: Decimal = angle ** sin_power
        sin_factorial_: Decimal = factorial(value=sin_power)
        sin_term: Decimal = sin_angle_power / sin_factorial_
        cos_angle_power: Decimal = angle ** cos_power
        cos_factorial_: Decimal = factorial(value=cos_power)
        cos_term: Decimal = cos_angle_power / cos_factorial_

        if (leading_decimal_zeroes(sin_term) > decimal_digits_precision and
                leading_decimal_zeroes(cos_term) > decimal_digits_precision):
            break

        sin_value += sin_sign * sin_term
        cos_value += cos_sign * cos_term
        sin_sign *= Decimal(-1)
        sin_power += Decimal(2)
        cos_sign *= Decimal(-1)
        cos_power += Decimal(2)

    return sin_value, cos_value


def tan(angle: Decimal) -> Decimal:
    sin_, cos_ = sin_cos(angle=angle)
    tan_: Decimal = sin_ / cos_
    return tan_


def cot(angle: Decimal) -> Decimal:
    sin_, cos_ = sin_cos(angle=angle)
    cot_: Decimal = cos_ / sin_
    return cot_


def csc(angle: Decimal) -> Decimal:
    sin_: Decimal = sin(angle=angle)
    csc_: Decimal = 1 / sin_
    return csc_


def sec(angle: Decimal) -> Decimal:
    cos_: Decimal = cos(angle=angle)
    sec_: Decimal = 1 / cos_
    return sec_


# def asin(ratio: Decimal) -> Decimal:
#     """
#     Calculate the arcsine or sin^(-1) of a Decimal ratio using power series expansion.
#     """
#
#     if ratio.copy_abs() > Decimal("1"):
#         raise ValueError(f"Ratio '{ratio}' is not in range [-1; 1].")
#     elif ratio.copy_abs() == Decimal("1"):
#         return Decimal(math.pi / 2).copy_sign(ratio)
#     elif ratio.copy_abs() > Decimal("0.95"):
#         raise ValueError(f"Ratio '{ratio}' too close to 1 takes extremely long time to compute.")
#
#     decimal_digits_precision: int = getcontext().prec
#
#     asin_value: Decimal = Decimal(0)
#
#     power: int = 1
#
#     while True:
#         if power > 1:
#             uneven = range(1, power, 2)
#             even = range(2, power, 2)
#             uneven_product: Decimal = Decimal(reduce(mul, uneven, 1))
#             even_product: Decimal = Decimal(reduce(mul, even, 1))
#             multiplier: Decimal = uneven_product / even_product
#         else:
#             multiplier: Decimal = Decimal("1")
#
#         value: Decimal = (ratio ** Decimal(power)) / Decimal(power)
#         term: Decimal = multiplier * value
#
#         if leading_decimal_zeroes(term) > decimal_digits_precision:
#             break
#
#         asin_value += term
#         power += 2
#     return asin_value


def asin(ratio: Decimal) -> Decimal:
    asin_value: Decimal = Decimal(math.asin(float(ratio)))
    return asin_value


# def acos(ratio: Decimal) -> Decimal:
#     acos_value: Decimal = (PI / 2) - asin(ratio=ratio)
#     return acos_value


def acos(ratio: Decimal) -> Decimal:
    acos_value: Decimal = Decimal(math.acos(float(ratio)))
    return acos_value


# def atan(ratio: Decimal) -> Decimal:
#     """
#     Calculate the arcsine or sin^(-1) of a Decimal ratio using power series expansion.
#     """
#
#     if ratio.copy_abs() > Decimal("1"):
#         raise ValueError(f"Ratio '{ratio}' is not in range [-1; 1].")
#     elif ratio.copy_abs() == Decimal("1"):
#         return Decimal(math.pi / 4).copy_sign(ratio)
#     elif ratio.copy_abs() == Decimal("0"):
#         return Decimal(0).copy_sign(ratio)
#     elif ratio.copy_abs() > Decimal("0.95"):
#         raise ValueError(f"Ratio '{ratio}' too close to 1 takes extremely long time to compute.")
#
#     decimal_digits_precision: int = getcontext().prec
#
#     atan_value: Decimal = ratio
#
#     sign: int = -1
#     power: int = 3
#
#     while True:
#         # if power > 1:
#         #     uneven = range(1, power, 2)
#         #     even = range(2, power, 2)
#         #     uneven_product: Decimal = Decimal(reduce(mul, uneven, 1))
#         #     even_product: Decimal = Decimal(reduce(mul, even, 1))
#         #     multiplier: Decimal = uneven_product / even_product
#         # else:
#         #     multiplier: Decimal = Decimal("1")
#
#         value: Decimal = (ratio ** Decimal(power)) / Decimal(power)
#         term: Decimal = sign * value
#
#         if leading_decimal_zeroes(term) > decimal_digits_precision:
#             break
#
#         atan_value += term
#         sign *= -1
#         power += 2
#     return atan_value


# def atan(ratio: Decimal) -> Decimal:
#     """
#     Calculate the arcsine or sin^(-1) of a Decimal ratio using power series expansion.
#     """
#
#     # if ratio.copy_abs() > Decimal("1"):
#     #     raise ValueError(f"Ratio '{ratio}' is not in range [-1; 1].")
#     if ratio == Decimal("Infinity"):
#         return Decimal(math.pi / 2)
#     elif ratio == Decimal("-Infinity"):
#         return -Decimal(math.pi / 2)
#     # elif ratio.copy_abs() == Decimal("1"):
#     #     return Decimal(math.pi / 4).copy_sign(ratio)
#     # elif ratio.copy_abs() == Decimal("0"):
#     #     return Decimal(0).copy_sign(ratio)
#     # elif ratio.copy_abs() > Decimal("0.95"):
#     #     raise ValueError(f"Ratio '{ratio}' too close to 1 takes extremely long time to compute.")
#
#     decimal_digits_precision: int = getcontext().prec
#
#     square_ratio: Decimal = ratio ** 2
#     divider: Decimal = 1 + square_ratio
#     atan_value: Decimal = ratio / divider
#
#     power: int = 3
#
#     while True:
#         # uneven = range(1, power, 2)
#         # even = range(2, power, 2)
#         # uneven_product: Decimal = Decimal(reduce(mul, uneven, 1))
#         # even_product: Decimal = Decimal(reduce(mul, even, 1))
#         # multiplier: Decimal = even_product / uneven_product
#         multiplier: Decimal = Decimal(power - 1) / Decimal(power)
#
#         value: Decimal = multiplier * (square_ratio / divider)
#         term: Decimal = atan_value * value
#
#         if leading_decimal_zeroes(term) > decimal_digits_precision:
#             break
#
#         atan_value += term
#         power += 2
#     return atan_value


def atan(ratio: Decimal) -> Decimal:
    atan_value: Decimal = Decimal(math.atan(float(ratio)))
    return atan_value


def asec(ratio: Decimal) -> Decimal:
    asec_value: Decimal = Decimal(math.acos(float(1/ratio)))
    return asec_value


def acsc(ratio: Decimal) -> Decimal:
    acsc_value: Decimal = Decimal(math.asin(float(1/ratio)))
    return acsc_value


def acot(ratio: Decimal) -> Decimal:
    acot_value: Decimal = Decimal(math.atan(float(1/ratio)))
    return acot_value


# TODO: create hyperbolic variations for trigonometry functions


# def atanh(ratio: Decimal) -> Decimal:
#     """
#     Calculate atanh(x) using log.
#     """
#
#     if ratio.copy_abs() > Decimal("1"):
#         raise ValueError(f"Ratio '{ratio}' is not in range [-1; 1].")
#
#     atanh_value: Decimal = Decimal("0.5") * ((Decimal("1") + ratio) / (Decimal("1") - ratio)).log10()
#
#     return atanh_value


def atan2(y: Decimal, x: Decimal) -> Decimal:
    atan2_value: Decimal = Decimal(math.atan2(float(y), float(x)))
    return atan2_value


def normalize_value(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    """Scale value position between minimum and maximum to [0:1] bound"""

    # Scale value and maximum relative to zero to enable finding fractional value by straightforward division
    zero_scaled_value: Decimal = value - minimum
    zero_scaled_maximum: Decimal = maximum - minimum

    # Divide scaled values
    normalized_value: Decimal = zero_scaled_value / zero_scaled_maximum

    return normalized_value


def clamp_or_normalize_value(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    new_value: Decimal

    if value < minimum:
        new_value = Decimal("0.0")
    elif value > maximum:
        new_value = Decimal("1.0")
    else:
        new_value = normalize_value(value=value, minimum=minimum, maximum=maximum)

    return new_value


def get_variability_amount(variability: Variability,
                           coloring_image_axis_size: Decimal) -> Decimal:
    if variability == Decimal("0.0"):
        variability_amount: Decimal = variability
    else:
        # TODO: get scaled or truncated value rather than retrying until value generated that fits in desired range
        #       search term: Truncated normal distribution
        # https://scipy.github.io/devdocs/reference/generated/scipy.stats.truncnorm.html
        # https://github.com/jessemzhang/tn_test/blob/master/truncated_normal/truncated_normal.py
        # package name: truncnorm
        # package name: pydistributions
        variation_value: Decimal = Decimal('Infinity')
        while variation_value < Decimal("-1.0") or variation_value > Decimal("1.0"):
            variation_value: Decimal = Decimal(normalvariate(mu=0.0, sigma=0.25))

        # Maximum extent of axis considered around point
        variability_radius: Decimal = variability * coloring_image_axis_size
        # Specific extent selected with normal distribution value
        variability_amount: Decimal = variation_value * variability_radius

    return variability_amount
