"""Internal fixed-point implementation module

MIT License

Copyright (c) 2024-Present Shachar Kraus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import contextlib
import copy
import dataclasses
import enum
import math
import mpmath
import numpy
import threading
from typing_extensions import Self
import warnings

# Basic classes


class FixedRounding(enum.Enum):
    """Rounding modes.
       See https://en.wikipedia.org/wiki/Rounding#Rounding_to_integer.
    """

    FLOOR = enum.auto()
    CEIL = enum.auto()
    TRUNC = enum.auto()
    AWAY = enum.auto()
    ROUND_HALF_DOWN = enum.auto()
    ROUND_HALF_UP = enum.auto()
    ROUND_HALF_TO_ZERO = enum.auto()
    ROUND_HALF_AWAY = enum.auto()
    ROUND_HALF_TO_EVEN = enum.auto()
    ROUND_HALF_TO_ODD = enum.auto()


class FixedBehavior(enum.Enum):
    """Behavior on error.

    IGNORE - ignore the error.
    STICKY - toggle a sticky flag.
    RAISE - raise an exception.

    """

    IGNORE = enum.auto()
    STICKY = enum.auto()
    RAISE = enum.auto()


@dataclasses.dataclass
class FixedState:
    """Fixed-point runtime state.
       Controls global fixed-point behavior.
    """

    rounding: FixedRounding = FixedRounding.ROUND_HALF_TO_EVEN
    modulo_rounding: FixedRounding = FixedRounding.TRUNC

    overflow_behavior: FixedBehavior = FixedBehavior.RAISE
    underflow_behavior: FixedBehavior = FixedBehavior.RAISE
    undefined_behavior: FixedBehavior = FixedBehavior.RAISE

    overflow_sticky: bool = False
    underflow_sticky: bool = False
    undefined_sticky: bool = False


class FixedOverflow(ArithmeticError):
    pass


class FixedUnderflow(ArithmeticError):
    pass


class FixedUndefined(ArithmeticError):
    pass


EXCEPTIONS_DICT = {
    'overflow': FixedOverflow,
    'underflow': FixedUnderflow,
    'undefined': FixedUndefined
}

# Globals


# Provides the default state, which matches IEEE-754
DEFAULT_FIXED_STATE = FixedState(
    FixedRounding.ROUND_HALF_TO_EVEN,
    FixedRounding.TRUNC,  # Matches fmod
    FixedBehavior.RAISE,
    FixedBehavior.RAISE,
    FixedBehavior.RAISE
)

# State management

# The thread-specific fixed state
fixed_tls = threading.local()
fixed_tls.current_fixed_state = copy.copy(DEFAULT_FIXED_STATE)


def get_fixed_state() -> FixedState:
    """Retrieves a copy of current thread's fixed state

    Returns:
        FixedState: State
    """

    return copy.copy(getattr(fixed_tls, 'current_fixed_state', DEFAULT_FIXED_STATE))


def set_fixed_state(state: FixedState) -> None:
    """Changes the current state

    Args:
        state (FixedState): New state
    """

    global fixed_tls

    fixed_tls.current_fixed_state = copy.copy(state)


@contextlib.contextmanager
def with_state(state: FixedState) -> FixedState:
    """Changes the current state within a 'with' block

    Args:
        state (FixedState): New state

    Yields:
        FixedState: New state
    """

    global fixed_tls

    old_state = get_fixed_state()
    fixed_tls.current_fixed_state = copy.copy(state)
    try:
        yield copy.copy(fixed_tls.current_fixed_state)
    finally:
        fixed_tls.current_fixed_state = old_state


def partial_state(
    rounding: FixedRounding = None,
    modulo_rounding: FixedRounding = None,
    overflow_behavior: FixedBehavior = None,
    underflow_behavior: FixedBehavior = None,
    undefined_behavior: FixedBehavior = None,
    overflow_sticky: bool = None,
    underflow_sticky: bool = None,
    undefined_sticky: bool = None
) -> None:
    """Partially changes the current state

    Args:
        rounding (FixedRounding, optional): _description_. Defaults to None.
        modulo_rounding (FixedRounding, optional): _description_. Defaults to None.
        overflow_behavior (FixedBehavior, optional): Behavior on overflow. Defaults to None.
        underflow_behavior (FixedBehavior, optional): Behavior on underflow. Defaults to None.
        undefined_behavior (FixedBehavior, optional): Behavior on undefined. Defaults to None.
        overflow_sticky (bool, optional): Overflow sticky bit. Defaults to None.
        underflow_sticky (bool, optional): Underflow sticky bit. Defaults to None.
        undefined_sticky (bool, optional): Undefined sticky bit. Defaults to None.

    Note: sticky bits are cleared on write to behavior (even if the behavior didn't change)
    """

    global fixed_tls

    if not hasattr(fixed_tls, 'current_fixed_state'):
        set_fixed_state(DEFAULT_FIXED_STATE)

    if rounding is not None:
        fixed_tls.current_fixed_state.rounding = rounding
    if modulo_rounding is not None:
        fixed_tls.current_fixed_state.modulo_rounding = modulo_rounding

    if overflow_behavior is not None:
        fixed_tls.current_fixed_state.overflow_behavior = overflow_behavior
        fixed_tls.current_fixed_state.overflow_sticky = False
    if underflow_behavior is not None:
        fixed_tls.current_fixed_state.underflow_behavior = underflow_behavior
        fixed_tls.current_fixed_state.underflow_sticky = False
    if undefined_behavior is not None:
        fixed_tls.current_fixed_state.undefined_behavior = undefined_behavior
        fixed_tls.current_fixed_state.undefined_sticky = False

    if overflow_sticky is not None:
        fixed_tls.current_fixed_state.overflow_sticky = overflow_sticky
    if underflow_sticky is not None:
        fixed_tls.current_fixed_state.underflow_sticky = underflow_sticky
    if undefined_sticky is not None:
        fixed_tls.current_fixed_state.undefined_sticky = undefined_sticky


@contextlib.contextmanager
def with_partial_state(
    rounding: FixedRounding = None,
    modulo_rounding: FixedRounding = None,
    overflow_behavior: FixedBehavior = None,
    underflow_behavior: FixedBehavior = None,
    undefined_behavior: FixedBehavior = None,
    overflow_sticky: bool = None,
    underflow_sticky: bool = None,
    undefined_sticky: bool = None
) -> FixedState:
    """Partially changes the current state within a 'with' block

    Args:
        rounding (FixedRounding, optional): _description_. Defaults to None.
        modulo_rounding (FixedRounding, optional): _description_. Defaults to None.
        overflow_behavior (FixedBehavior, optional): Behavior on overflow. Defaults to None.
        underflow_behavior (FixedBehavior, optional): Behavior on underflow. Defaults to None.
        undefined_behavior (FixedBehavior, optional): Behavior on undefined. Defaults to None.
        overflow_sticky (bool, optional): Overflow sticky bit. Defaults to None.
        underflow_sticky (bool, optional): Underflow sticky bit. Defaults to None.
        undefined_sticky (bool, optional): Undefined sticky bit. Defaults to None.

    Yields:
        FixedState: New state
    """

    global fixed_tls

    old_state = get_fixed_state()
    partial_state(
        rounding,
        modulo_rounding,
        overflow_behavior,
        underflow_behavior,
        undefined_behavior,
        overflow_sticky,
        underflow_sticky,
        undefined_sticky
    )
    try:
        yield copy.copy(fixed_tls.current_fixed_state)
    finally:
        fixed_tls.current_fixed_state = old_state


def get_sticky(*args, clear=False) -> bool | tuple:
    """Retrieves sticky bits and optionally clears them

    Args:
        ... (str, optional): Bit names to retrieve.
                   Can be 'overflow', 'underflow' and 'undefined'.
                   Defaults to all of them.
        clear (bool, optional): Clear retrieved bits. Defaults to False.

    Raises:
        ValueError: Invalid bit name

    Returns:
        bool | tuple: Bit value(s)

    Examples:
        get_sticky(): returns all sticky bits (overflow, underflow, undefined).
        get_sticky(clear=True): returns all sticky bits and clears them.
        get_sticky('overflow'): returns the overflow bit.
        get_sticky('overflow', 'underflow'): returns the overflow and underflow bits.
        get_sticky('underflow', 'overflow'): returns the underflow and overflow bits (in this order).
    """

    options = ('overflow', 'underflow', 'undefined')

    if len(args) == 0:
        args = options

    state = get_fixed_state()

    ret = []
    kwargs = {}
    for bit in args:
        if bit not in options:
            raise ValueError(f'Invalid bit name "{bit}"')

        key = bit + '_sticky'
        ret.append(state.__dict__[key])

        if clear:
            kwargs[key] = False

    if clear:
        partial_state(**kwargs)

    return tuple(ret) if len(ret) > 1 else ret[0]


def trigger_error(error: str, except_str: str = None) -> None:
    """For internal use only.
       Triggers an error.

    Args:
        error (str): Error name.
        except_str (str, optional): Exception string. Defaults to None.

    Raises:
        FixedOverflow
        FixedUnderflow
        FixedUndefined
    """

    behavior = get_fixed_state().__dict__[error + '_behavior']

    if behavior == FixedBehavior.RAISE:
        raise EXCEPTIONS_DICT[error](except_str)
    elif behavior == FixedBehavior.STICKY:
        partial_state(**{error + '_sticky': True})
    # else ignore

# Fixed


def float_round(x: mpmath.mpf, check_underflow: bool = True) -> int:
    """Rounds a float

    Args:
        x (mpmath.mpf): Float to round
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUnderflow: Result underflow

    Returns:
        int: Result
    """

    result = x

    rounding = get_fixed_state().rounding

    if rounding == FixedRounding.CEIL                     \
            or (rounding == FixedRounding.TRUNC and x < 0)\
            or (rounding == FixedRounding.AWAY and x >= 0):
        result = mpmath.ceil(result)
        # For truncation, if x >= 0, floor will be used.
        # For away, if x < 0, floor will be used.
    else:
        if rounding == FixedRounding.ROUND_HALF_UP                         \
                or (x < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
                or (x >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
            result += 0.5
        elif rounding == FixedRounding.ROUND_HALF_DOWN                      \
                or (x >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
                or (x < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
            if result % 1 != 0.5:
                result += 0.5
        elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
            if (result % 2) != 0.5:
                result += 0.5
        elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
            if (result % 2) != 1.5:
                result += 0.5
        # else floor
        result = mpmath.floor(result)

    if check_underflow and result == 0 and x != 0:
        trigger_error('underflow')

    return result


def prepare_round(x: int, bit: int, rounding: FixedRounding = None) -> int:
    """Prepares a number for rounding via a floor operation

    Args:
        x (int): Number to prepare
        bit (int): Bit index where the number will be rounded at
        rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.

    Returns:
        int: Prepared number
    """

    if bit <= 0:
        return x

    if rounding is None:
        rounding = get_fixed_state().rounding

    epsilon = 1
    half = 1 << (bit - 1)
    one = 1 << bit
    one_and_half = 3 << (bit - 1)
    one_and_half_mask = (one << 1) - 1

    if rounding == FixedRounding.CEIL                     \
            or (rounding == FixedRounding.TRUNC and x < 0)\
            or (rounding == FixedRounding.AWAY and x >= 0):
        x += one - epsilon
        # For truncation, if x >= 0, floor will be used.
        # For away, if x < 0, floor will be used.
    elif rounding == FixedRounding.ROUND_HALF_UP                       \
            or (x < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (x >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        x += half
    elif rounding == FixedRounding.ROUND_HALF_DOWN                      \
            or (x >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (x < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        x += half - epsilon
    elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
        if (x & one_and_half_mask) != half:
            x += half
    elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
        if (x & one_and_half_mask) != one_and_half:
            x += half
    # else floor

    return x


def shift_round(
    x: int,
    shift: int,
    rounding: FixedRounding = None,
    check_underflow: bool = True
) -> int:
    """Shifts (divides by a power of 2) with rounding

    Args:
        x (int): Number to divide
        shift (int): Bits to shift by. Shifts left (i.e. divides by 2 ** shift).
        rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUnderflow: Result underflow

    Returns:
        int: Result
    """

    if shift <= 0:
        return x << (-shift)

    result = prepare_round(x, shift, rounding=rounding) >> shift  # Floors
    if check_underflow and result == 0 and x != 0:
        trigger_error('underflow')

    return result


def div_round(
    dividend: int,
    divider: int,
    rounding: FixedRounding = None,
    check_underflow: bool = True
) -> int:
    """Divides and rounds the result

    Args:
        dividend (int): Number to divide
        divider (int): Number to divide by
        rounding (FixedRounding, optional): Rounding mode. Defaults to current's state's mode.
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUndefined: Divide by 0
        FixedUnderflow: Result underflow

    Returns:
        int: Result
    """

    if divider == 0:
        trigger_error('undefined', 'Divide by 0')
        return 0

    if rounding is None:
        rounding = get_fixed_state().rounding

    if divider < 0:
        dividend = -dividend
        divider = -divider

    if divider == 1:
        # No rounding required, and also breaks "epsilon = 1"
        return dividend

    epsilon = 1
    half = divider // 2
    one = divider
    one_and_half = 3 * divider // 2

    result = dividend

    if rounding == FixedRounding.CEIL \
            or (rounding == FixedRounding.TRUNC and dividend < 0)\
            or (rounding == FixedRounding.AWAY and dividend >= 0):
        result += one - epsilon
        # For truncation, if dividend >= 0, floor will be used.
        # For away, if dividend < 0, floor will be used.
    elif rounding == FixedRounding.ROUND_HALF_UP                              \
            or (dividend < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (dividend >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        result += half
    elif rounding == FixedRounding.ROUND_HALF_DOWN                             \
            or (dividend >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (dividend < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        # result += half - (epsilon if divider is even else 0)
        result += half - ((divider & 1) ^ 1)
    elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
        if (dividend % (2 * divider)) != half:
            result += half
    elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
        if (dividend % (2 * divider)) != one_and_half:
            result += half
    # else floor

    result //= divider  # Floors
    if check_underflow and result == 0 and dividend != 0:
        trigger_error('underflow')

    return result


def semi_fixed(x: mpmath.mpf) -> tuple:
    """Converts a float to a semi-fixed number

    Args:
        x (mpmath.mpf): Value to convert

    Returns:
        mantissa (int): Semi-fixed internal value
        exp (int): Semi-fixed fraction bits
        e (int): Original exponent value
        mantissa / 2 ** exp = x
        mantissa / 2 ** mpmath.mp.prec * 2 ** e = x
    """

    # Convert to semi-fixed using frexp

    # frexp splits x to mantissa and exponent, where 0 <= mantissa < 1 or mantissa = 0:
    # x = mantissa * 2 ** exponent
    # We want the mantissa to be 0 <= mantissa < 2 ** (M + 1) (which is like fixed-point with M
    # fraction bits).
    #
    # Note that unless x = 0, the mantissa will always have the highest bit set (the always-1 bit).
    # So we want the range [2 ** M, 2 ** (M + 1)), representing numbers in [1, 2).
    # Achieving that is done via multiplication by 2 ** (M + 1):
    # 0.5 * 2 ** (M + 1) <= mantissa * 2 ** (M + 1) < 1 * 2 ** (M + 1)
    # 2 ** M <= mantissa * 2 ** (M + 1) < 2 ** (M + 1)
    # We then subtract 1 from the exponent to ensure that x = mantissa * 2 ** exponent.

    if x == 0:
        return 0, 0, 0

    M = mpmath.mp.prec

    m, e = mpmath.frexp(x)  # Returns [0.5, 1)
    e -= 1

    mantissa = int(mpmath.ldexp(m, M + 1))
    exp = M - e

    return mantissa, exp, e


class FixedProperties:
    """Shared storage for fixed-point objects
    """

    properties = {}

    @staticmethod
    def _key_from_bits(fraction_bits: int, integer_bits: int, sign: bool) -> int:
        """
        Converts fixed bits to an access key for the dictionary

        Args:
            fraction_bits (int): Number of fraction bits
            integer_bits (int): Number of integer bits
            sign (bool): Signedness

        Returns:
            int: Access key
        """

        return hash((fraction_bits, integer_bits, sign))

    def __init__(self, fraction_bits: int, integer_bits: int, sign: bool):
        """Initializes the properties class.
           Internal use only!
           Use get_property_class instead!

        Args:
            fraction_bits (int): Number of fraction bits
            integer_bits (int): Number of integer bits
            sign (bool): Signedness
        """

        # Initialize

        self.fraction_bits = fraction_bits
        self.integer_bits = integer_bits
        self.sign = sign

        bits = fraction_bits + integer_bits

        self._min_val = -(1 << bits) if sign else 0
        self._max_val = (1 << bits) - 1
        self.epsilon = 1 if bits else 0
        self.half = (1 << (fraction_bits - 1)) if fraction_bits else 0
        self.one = 1 << fraction_bits

        self.human_format = 'Fixed<' \
            f'{self.fraction_bits}, '\
            f'{self.integer_bits}, ' \
            f'{"signed" if self.sign else "unsigned"}>'

        # Add to the dictionary
        FixedProperties.properties[
            FixedProperties._key_from_bits(
                fraction_bits,
                integer_bits,
                sign
            )
        ] = self

    @staticmethod
    def get_property_class(fraction_bits: int, integer_bits: int, sign: bool) -> Self:
        """Retrieves a property class

        Args:
            fraction_bits (int): Number of fraction bits
            integer_bits (int): Number of integer bits
            sign (bool): Signedness

        Returns:
            FixedProperty: Properties
        """

        # Avoid pollution of incompatible types (they can later appear in Python integer
        # operations, e.g. x << y which results in numpy.integer instead of int)
        fraction_bits = int(fraction_bits)
        integer_bits = int(integer_bits)
        sign = bool(sign)

        key = FixedProperties._key_from_bits(fraction_bits, integer_bits, sign)

        if key not in FixedProperties.properties:
            FixedProperties(fraction_bits, integer_bits, sign)

        return FixedProperties.properties[key]


class Fixed:

    @property
    def fraction_bits(self):
        return self.properties.fraction_bits

    @property
    def integer_bits(self):
        return self.properties.integer_bits

    @property
    def sign(self):
        return self.properties.sign

    @property
    def _min_val(self):
        return self.properties._min_val

    @property
    def _max_val(self):
        return self.properties._max_val

    @property
    def epsilon(self):
        return self.properties.epsilon

    @property
    def half(self):
        return self.properties.half

    @property
    def one(self):
        return self.properties.one

    @property
    def human_format(self) -> str:
        """Provides a human-readable fixed-point string of this class

        Returns:
            str: Fixed-point format
        """

        return self.properties.human_format

    def _clip(self, value):
        """Clips a value to the class' range

        Args:
            value: Value to clip
            process_state (bool, optional): Process exceptions. Defaults to true.

        Raises:
            FixedOverflow: Value is out of the supported range

        Returns:
            Clipped value
        """

        self.value = int(max(min(value, self._max_val), self._min_val))

        if self.value != value:
            trigger_error(
                'overflow',
                f'Value "{value}" (internal) overflows out of {self.human_format}'
            )

    def _create_same(self, value=None, internal: bool = True) -> Self:
        """Creates a fixed-point number of the same configuration as self

        Args:
            value (any, optional): Initial value. Defaults to None.
            internal (bool, optional): Value is the internal value. Defaults to True.

        Returns:
            Fixed: New fixed-point number
        """

        return Fixed(value, self.fraction_bits, self.integer_bits, self.sign, internal=internal)

    def _create_copy(self) -> Self:
        """Creates a copy of this number

        Returns:
            Fixed: Copy
        """

        return self._create_same(self.value)

    def _create_common(self, other: Self, value: int = None, internal: bool = False) -> Self:
        """Creates a number in a common precision

        Args:
            other (Fixed): Other fixed
            value (int, optional): Initial value. Defaults to None.
            internal (bool, optional): Value is the internal value. Defaults to False.

        Returns:
            Fixed: Common precision number
        """

        return Fixed(
            value,
            fraction_bits=max(self.fraction_bits, other.fraction_bits),
            integer_bits=max(self.integer_bits, other.integer_bits),
            sign=self.sign or other.sign,
            internal=internal
        )

    def _common_copy(self, other: Self) -> Self:
        """Creates a copy of self in a common precision

        Args:
            other (Fixed): Other fixed

        Returns:
            Fixed: Common precision copy
        """

        return self._create_common(other, self)

    def _common_precision(self, other_val: int, other_prec: int, op, scale_back=True) -> int:
        """Performs an operation in common precision

        Args:
            other_val (int): Other integer value
            other_prec (int): Other value's precision (fraction bits)
            op (function): Operation to perform
            scale_back (bool, optional): Scale the result back to self's format. Defaults to True.

        Raises:
            FixedUnderflow: Underflow detected when converting to self's format

        Returns:
            int: Result
        """

        diff = self.fraction_bits - other_prec

        self_reg = self.value
        other_reg = other_val

        # Bring both to the same precision
        if diff < 0:
            self_reg <<= -diff
        else:
            other_reg <<= diff

        # Perform the operation
        result = op(self_reg, other_reg)

        # Scale if required
        if scale_back and diff < 0:
            result = shift_round(result, -diff)

        return result

    def _higher_precision(self) -> Self:
        """Creates a higher precision copy of this number

        Returns:
            Fixed: Higher precision copy
        """

        return promote(self)(self)

    def _to_generic_float(self, ldexp, prec: int):
        """Casts to a float

        Args:
            ldexp (function): Float's ldexp function
            prec (int): Float's precision (mantissa bits, including always-1)

        Returns:
            Casted float
        """

        # Return self.value / 2 ** self.fraction_bits
        bits = self.fraction_bits + self.integer_bits

        mantissa = self.value
        exponent = -self.fraction_bits

        if prec < bits:
            # The mantissa won't fit in the format, so we remove LSBs via rounding.
            mantissa = shift_round(mantissa, bits - prec)
            exponent += bits - prec

        return ldexp(mantissa, exponent)

    def _floor(self) -> None:
        """Floors self
        """
        self.value &= -self.one

    def _handle_underflow_rounding(
        self,
        other: mpmath.mpf,
        rounding: FixedRounding = None,
        scale: int = 0
    ) -> None:
        """Handles rounding where self is added with a very small float

        Args:
            other (mpmath.mpf): Very small float
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            scale (int, optional): Scales (shifts) the number. Defaults to 0 (no scaling).

        Note: other's value is ignored, only the sign is taken into account
        """

        self._clip(
            shift_round(
                (self.value << 2) + int(mpmath.sign(other)),
                2,
                rounding=rounding,
                check_underflow=False
            ) << scale
        )

    def _div(
        self,
        other,
        rounded_bits: int = 0,
        rounding: FixedRounding = None,
        check_underflow: bool = True
    ) -> Self:
        """Divides self by a number

        Args:
            other (any): Divider
            rounded_bits (int, optional): Bits to round, starting from LSB. Defaults to 0 (normal rounding).
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            check_underflow (bool, optional): Check for underflow. Defaults to True.

        Returns:
            Fixed: result (self or NotImplemented)
        """

        def implementation(val: int, fract: int) -> None:
            # Shift left and divide

            # a / 2 ** N / (b / 2 ** M) = x / 2 ** N
            # a / b / 2 ** N * 2 ** M = x / 2 ** N
            # x = a / b * 2 ** M

            a = self.value
            b = val
            diff = fract - rounded_bits

            if diff >= 0:
                a <<= diff
            else:
                b <<= -diff

            self._clip(
                div_round(
                    a,
                    b,
                    rounding=rounding,
                    check_underflow=check_underflow
                ) << rounded_bits
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.integer)):
            # Cast to int because NumPy integers are limited
            implementation(int(other), 0)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self._div(
                    mpmath.mpmathify(other),
                    rounded_bits=rounded_bits,
                    rounding=rounding,
                    check_underflow=check_underflow
                )
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                trigger_error(
                    'underflow',
                    f'Underflow: operation on {self.human_format} and {other}'
                )
                self.value = 0
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = 0
            elif other:  # Undefined if other == 0
                if self.value:
                    # Limits are similar to __iadd__ and __imul__:
                    #
                    # Overflow:
                    # |self / other| <= 2 ** integer_bits
                    # |other| >= |self| / 2 ** integer_bits
                    # Get the minimal value for |self| / 2 ** integer_bits
                    # by assigning |self| = 2 ** -fraction_bits:
                    # |other| >= 2 ** -fraction_bits * 2 ** -integer_bits
                    # |other| >= 2 ** -(fraction_bits + integer_bits)
                    #
                    # Underflow:
                    # |self / other| >= 2 ** -(fraction_bits + 1)
                    # |other| <= |self| * 2 ** (fraction_bits + 1)
                    # Get the maximal value for |self| / 2 ** (fraction_bits + 1)
                    # by assigning |self| = 2 ** integer_bits:
                    # |other| <= 2 ** integer_bits * 2 ** (fraction_bits + 1)
                    # |other| <= 2 ** (integer_bits + fraction_bits + 1)
                    #
                    # Final limits:
                    # 2 ** -(fraction_bits + integer_bits) <= |other| <= 2 ** (integer_bits + fraction_bits + 1)
                    # Using frexp, we get -fraction_bits - integer_bits <= exponent <= integer_bits + fraction_bits + 1

                    mantissa, exp, e = semi_fixed(other)

                    if e < -self.fraction_bits - self.integer_bits:
                        trigger_error(
                            'overflow',
                            f'Overflow: 1 / {other} is too big for {self.human_format}'
                        )
                        # Silent overflow
                        self.value = self._max_val if (self.value >= 0) == (
                            other >= 0) else self._min_val
                    elif e > self.integer_bits + self.fraction_bits + 1:
                        if check_underflow:
                            trigger_error(
                                'underflow',
                                f'Underflow: 1 / {other} is too small for {self.human_format}'
                            )
                        # Silent underflow
                        sign = mpmath.sign(self.value) * mpmath.sign(other)
                        self.value = 0
                        self._handle_underflow_rounding(sign, rounding=rounding, scale=rounded_bits)
                    else:
                        # Calculate like in fixed
                        implementation(mantissa, exp)
                else:
                    self.value = 0
            else:
                trigger_error('undefined', 'Divide by 0')
                self.value = 0
        else:
            return NotImplemented

        return self

    def _reverse_div(
        self,
        other,
        rounded_bits: int = 0,
        rounding: FixedRounding = None,
        check_underflow: bool = True
    ) -> Self:
        """Divides a number by self

        Args:
            other (any): Dividend
            rounded_bits (int, optional): Bits to round, starting from LSB. Defaults to 0 (normal rounding).
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            check_underflow (bool, optional): Check for underflow. Defaults to True.

        Returns:
            Result (or NotImplemented)
        """

        # Note: other can't be Fixed

        def implementation(val: int, fract: int) -> Fixed:
            # a / 2 ** N / (b / 2 ** M) = x / 2 ** N
            # a / b / 2 ** N * 2 ** M = x / 2 ** N
            # x = a / b * 2 ** M

            a = self.value
            b = val
            diff = 2 * self.fraction_bits - fract - rounded_bits

            if diff <= 0:
                a <<= -diff
            else:
                b <<= diff

            return self._create_same(
                div_round(
                    b,
                    a,
                    rounding=rounding,
                    check_underflow=check_underflow
                ) << rounded_bits
            )

        if isinstance(other, Fixed):
            return NotImplemented
        elif isinstance(other, (bool, int, numpy.integer)):
            # Cast to int because NumPy integers are limited
            return implementation(int(other), 0)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self._reverse_div(
                    mpmath.mpmathify(other),
                    rounded_bits=rounded_bits,
                    rounding=rounding,
                    check_underflow=check_underflow
                )
        elif isinstance(other, mpmath.mpf):
            if mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                return self._create_same()
            elif self.value:  # Undefined if self == 0
                if mpmath.isinf(other):
                    trigger_error(
                        'overflow',
                        f'Overflow: operation on {self.human_format} and {other}'
                    )
                    return self._create_same(
                        self._max_val
                        if (other > 0) == (self.value > 0)
                        else self._min_val
                    )
                elif other:
                    # Limits are similar to __iadd__, __imul__ and __itruediv__:
                    #
                    # Overflow:
                    # |other / self| <= 2 ** integer_bits
                    # |other| <= 2 ** integer_bits * |self|
                    # Choose |self| = 2 ** integer_bits
                    # |other| <= 2 ** (2 * integer_bits)
                    #
                    # Underflow:
                    # |other / self| >= 2 ** -(fraction_bits + 1)
                    # |other / self| >= 2 ** -(fraction_bits + 1)
                    # |other| >= |self| / 2 ** (fraction_bits + 1)
                    # Choose |self| = 2 ** -fraction_bits
                    # |other| >= 2 ** -(2 * fraction_bits + 1)
                    #
                    # Final limits:
                    # 2 ** -(2 * fraction_bits + 1) <= |other| <= 2 ** (2 * integer_bits)
                    # Using frexp, we get -2 * fraction_bits - 1 <= exponent <= 2 * integer_bits

                    mantissa, exp, e = semi_fixed(other)

                    if e > 2 * self.integer_bits:
                        trigger_error(
                            'overflow',
                            f'Overflow: {other} is too big for {self.human_format}'
                        )
                        # Silent overflow
                        return self._create_same(self._max_val if (self.value >= 0) == (other >= 0) else self._min_val)
                    elif e < -2 * self.fraction_bits - 1:
                        if check_underflow:
                            trigger_error(
                                'underflow',
                                f'Underflow: {other} is too small for {self.human_format}'
                            )
                        # Silent underflow
                        result = self._create_same()
                        result._handle_underflow_rounding(
                            mpmath.sign(self.value) * mpmath.sign(other),
                            rounding=rounding,
                            scale=rounded_bits
                        )
                        return result
                    else:
                        # Calculate like in fixed
                        return implementation(mantissa, exp)
                else:
                    return self._create_same()
            else:
                trigger_error('undefined', 'Divide by 0')
                return self._create_same()
        else:
            return NotImplemented

    def __init__(
        self,
        value:
            bool |
            int |
            float |
            complex |
            numpy.integer |
            numpy.floating |
            numpy.complexfloating |
            mpmath.mpf |
            mpmath.mpc |
            Self
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        internal: bool = False
    ):
        """Initializes a new fixed-point number

        Args:
            value (
                bool,
                int,
                float,
                complex,
                numpy.integer,
                numpy.floating,
                numpy.complexfloating,
                mpmath.mpf,
                mpmath.mpc,
                Fixed,
                ComplexFixed,
                optional
            ): Initial value. Defaults to None.
            fraction_bits (int, optional): Number of fraction bits. Defaults to 53.
            integer_bits (int, optional): Number of integer bits. Defaults to 10.
            sign (bool, optional): Signedness. Defaults to True.
            internal (bool, optional): Directly store the initial value. Defaults to False.
        """

        # Convert complex to real
        if hasattr(value, 'imag'):
            if value.imag != 0:
                warnings.warn(
                    numpy.exceptions.ComplexWarning(
                        'Casting complex values to real discards the imaginary part'
                    ),
                    stacklevel=2
                )
            value = value.real

        # Deduce configuration
        if fraction_bits is None:
            fraction_bits = value.fraction_bits if isinstance(value, Fixed) else 52
        if integer_bits is None:
            integer_bits = value.integer_bits if isinstance(value, Fixed) else 11
        if sign is None:
            sign = value.sign if isinstance(value, Fixed) else True

        if fraction_bits < 0 or integer_bits < 0:
            raise TypeError("Bit amounts can't be negative")
        if fraction_bits + integer_bits + sign <= 0:
            raise TypeError('Fixed-point requires a non-zero number of bits')

        self.properties = FixedProperties.get_property_class(fraction_bits, integer_bits, sign)

        # Convert the value

        if value is None:
            self.value = 0
            return

        if isinstance(value, Fixed):
            # Round and clip
            self._clip(
                shift_round(
                    value.value,
                    0 if internal else (value.fraction_bits - self.fraction_bits)
                )
            )
        elif isinstance(value, (bool, int, numpy.integer)):
            # Cast to int because NumPy's integers are limited
            self._clip(int(value) << (0 if internal else self.fraction_bits))
        else:
            if mpmath.isinf(value):
                trigger_error('overflow', f'Initializing {self.human_format} from {value}')
                self.value = self._max_val if value > 0 else self._min_val
                return
            elif mpmath.isnan(value):
                trigger_error('undefined', f'Initializing {self.human_format} from {value}')
                self.value = 0
                return

            for t, p in (
                (float, numpy.finfo(numpy.float64).nmant + 1),

                (numpy.float32, numpy.finfo(numpy.float32).nmant + 1),
                (numpy.float64, numpy.finfo(numpy.float64).nmant + 1),
                # NumPy doesn't include the 1 bit, even for long double
                (numpy.float128, numpy.finfo(numpy.float128).nmant + 1),

                (mpmath.mpf, mpmath.mp.prec),
            ):
                if isinstance(value, t):
                    prec = p
                    break

            with mpmath.workprec(prec):
                self._clip(
                    float_round(
                        mpmath.ldexp(
                            mpmath.mpmathify(value),
                            (0 if internal else self.fraction_bits)
                        )
                    )
                )

    # Conversions

    def __bool__(self) -> bool:
        return bool(self.value)

    def __int__(self) -> int:
        return shift_round(self.value, self.fraction_bits, check_underflow=False)

    def __float__(self) -> float:
        return self._to_generic_float(math.ldexp, numpy.finfo(float).nmant + 1)

    def __complex__(self) -> complex:
        return complex(float(self))

    def __repr__(self) -> str:
        return self.human_format + str(self)

    def __str__(self) -> str:
        return f'{hex(self.value)}p{-self.fraction_bits}'

    def __format__(self) -> str:
        return str(self)

    def __bytes__(self) -> bytes:
        # Convert to an unsigned representation by calculating self.value % 2 ** bits
        bits = self.fraction_bits + self.integer_bits + self.sign
        return (self.value & ((1 << bits) - 1)).to_bytes(
            length=(bits + 7) // 8,  # ceil(bits / 8)
            byteorder='little'
        )

    def __array__(self, dtype_meta=numpy.dtypes.Float64DType, copy: bool = True) -> numpy.ndarray:
        """Converts to NumPy

        Args:
            dtype_meta (numpy._DTypeMeta, optional): dtype meta from NumPy.
                                                     Defaults to double.
            copy (bool, optional) Create a copy.
                                  Defaults to True.

        Raises:
            TypeError: copy=False

        Returns:
            numpy.ndarray: Converted value
        """

        dtype = dtype_meta.type

        if copy is False:
            raise TypeError(f'Casting Fixed to {dtype} requires creating a copy')

        if issubclass(dtype, numpy.complexfloating):
            dtype = type(numpy.real(dtype()))
        elif issubclass(dtype, numpy.integer):
            return numpy.array(dtype(int(self)))

        return numpy.array(
            self._to_generic_float(
                lambda x, p: numpy.ldexp(numpy.real(dtype(x)), p),
                numpy.finfo(dtype).nmant + 1
            )
        )

    def mpmath(self) -> mpmath.mpf:
        """Converts to mpmath.mpf

        Returns:
            mpmath.mpf: Converted value
        """

        return self._to_generic_float(mpmath.ldexp, mpmath.mp.prec)

    # Unary operators

    def __pos__(self) -> Self:
        return self._create_copy()

    def __neg__(self) -> Self:
        return self._create_same(-self.value)

    def __invert__(self) -> Self:
        return self._create_same(~self.value)

    def __abs__(self) -> Self:
        return self._create_copy() if self >= 0 else -self

    # Rounding

    def __floor__(self) -> int:
        return (self.value & -self.one) >> self.fraction_bits

    def __ceil__(self) -> int:
        if self.fraction_bits:
            return ((self.value + self.one - self.epsilon) & -self.one) >> self.fraction_bits
        else:
            return self.value

    def __trunc__(self) -> int:
        return math.floor(self) if self >= 0 else math.ceil(self)

    def __round__(self, ndigits: int = None):
        """Rounds the number

        Args:
            ndigits (int, optional): Round up to 'ndigits' digits after the point.
                                     Unlike conventional 'round', digits are binary.
                                     Defaults to None.

        Returns:
            int: Rounded number (ndigits == None)
            Fixed: Rounding number (ndigits != None, can be 0)
        """

        if ndigits is None:
            bit = self.fraction_bits
        else:
            if ndigits > self.fraction_bits:
                return self._create_copy()
            if ndigits < -(self.fraction_bits + self.integer_bits):
                return self._create_same()
            bit = self.fraction_bits - ndigits

        mask = -(1 << bit)
        result = prepare_round(self.value, bit) & mask
        return (result >> self.fraction_bits) if ndigits is None else self._create_same(result)

    # Binary operators

    # Addition

    def __iadd__(self, other) -> Self:
        if isinstance(other, Fixed):
            # Just add and clip
            self._clip(self._common_precision(other.value, other.fraction_bits, lambda a, b: a + b))
        elif isinstance(other, (bool, int, numpy.integer)):
            # Like above, but it's not fixed.
            # Cast to int because NumPy integers are limited.
            self._clip(self.value + (int(other) << self.fraction_bits))
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                self += mpmath.mpmathify(other)
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                trigger_error(
                    'overflow',
                    f'Overflow: operation on {self.human_format} and {other}'
                )
                self.value = self._max_val if other > 0 else self._min_val
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = 0
            elif other:  # 0 has a negative infinity exponent
                # We limit other in order to pre-determine overflow and underflow.
                # We could just add, but with a float big enough, shifts will become very
                # expensive (double has an exponent [-1022, 1023], long double has even more,
                # and mpmath could be too much).
                #
                # The overflow limit is -(2 ** integer_bits) <= self + other <= 2 ** integer_bits.
                # (Should be < 2 ** integer_bits but it's insignificant).
                # We need a value self which lets other have a maximal magnitude.
                # This value is -sign(other) * 2 ** integer_bits, and we get:
                # -(2 ** integer_bits) <= other - sign(other) * 2 ** integer_bits <= 2 ** integer_bits
                # If other is positive:
                # -(2 ** integer_bits) <= other - (2 ** integer_bits) <= 2 ** integer_bits
                # 0 <= other <= 2 ** (integer_bits + 1)
                # Otherwise:
                # -(2 ** integer_bits) <= other + 2 ** integer_bits <= 2 ** integer_bits
                # -(2 ** (integer_bits + 1)) <= other <= 0
                # In general: |other| <= 2 ** (integer_bits + 1)
                #
                # The underflow limit is |self + other| >= 2 ** -fraction_bits.
                # We lower the limit by halving it so that exact halves are rounded
                # according to the rounding configuration.
                # We get |self + other| >= 2 ** -(fraction_bits + 1).
                # This time, we choose self = 0, because no other value can result
                # in underflow to 0 (unless other = -self, but that's not an underflow).
                # The limit is therefore |other| >= 2 ** -(fraction_bits + 1).
                #
                # Finally, our limits are
                # 2 ** -(fraction_bits + 1) <= |other| <= 2 ** (integer_bits + 1)
                # Using frexp, we get -fraction_bits - 1 <= exponent <= integer_bits + 1

                mantissa, exp, e = semi_fixed(other)

                if e > self.integer_bits + 1:
                    trigger_error(
                        'overflow',
                        f'Overflow: {other} is too big for {self.human_format}'
                    )
                    # Just clip it
                    self.value = self._max_val if other >= 0 else self._min_val
                elif e < -self.fraction_bits - 1:
                    # Guaranteed underflow
                    trigger_error(
                        'underflow',
                        f'Underflow: {other} is too small for {self.human_format}'
                    )
                    # Either sticky or ignored, so we need to round properly
                    self._handle_underflow_rounding(other)
                else:
                    # Treat it like a fixed
                    self._clip(self._common_precision(mantissa, exp, lambda a, b: a+b))
        else:
            return NotImplemented

        return self

    def __add__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__iadd__(other)

    def __radd__(self, other):
        if isinstance(other, Fixed):
            return NotImplemented

        return self + other

    # Subtraction

    def __isub__(self, other) -> Self:
        if isinstance(other, Fixed):
            # Just subtract and clip
            self._clip(self._common_precision(other.value, other.fraction_bits, lambda a, b: a - b))
        elif isinstance(other, (bool, int, numpy.integer)):
            # Like above, but it's not fixed.
            # Cast to int because NumPy integers are limited.
            self._clip(self.value - (int(other) << self.fraction_bits))
        elif isinstance(other, (float, numpy.floating, mpmath.mpf)):
            self += -other  # Will raise NotImplemented
        else:
            return NotImplemented

        return self

    def __sub__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__isub__(other)

    def __rsub__(self, other) -> Self:
        # Note: other can't be Fixed

        if isinstance(other, (bool, int, numpy.integer)):
            # Create an intermediate representation and subtract
            return self._create_same((int(other) << self.fraction_bits) - self.value)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self.__rsub__(mpmath.mpmathify(other))
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                trigger_error(
                    'overflow',
                    f'Overflow: operation on {self.human_format} and {other}'
                )
                return self._create_same(self._max_val if other > 0 else self._min_val)
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {other} and {self.human_format}'
                )
                return self._create_same()
            elif other:  # 0 has a negative infinity exponent
                # Limits calculation is similar to __iadd__

                mantissa, exp, e = semi_fixed(other)

                if e > self.integer_bits + 1:
                    trigger_error(
                        'overflow',
                        f'Overflow: {other} is too big for {self.human_format}'
                    )
                    # Just clip it
                    return self._create_same(self._max_val if other >= 0 else self._min_val)
                elif e >= -self.fraction_bits - 1:
                    # Treat it like a fixed
                    return self._create_same(self._common_precision(mantissa, exp, lambda a, b: b - a))
                # Else guaranteed underflow.
                # However, we might have and overflow as well - it
                # should be prioritized because it modifies the value.

            # Return 0 - self

            retval = -Fixed(
                self,
                fraction_bits=self.fraction_bits,
                integer_bits=self.integer_bits + 1,
                sign=True
            )

            if other != 0:
                # Process overflow before underflow
                retval._handle_underflow_rounding(other)
                if retval.value > self._max_val or retval.value < self._min_val:
                    trigger_error(
                        'overflow',
                        f'Overflow: {retval.value} (internal) is too big for {self.human_format}'
                    )

                # Trigger underflow
                trigger_error(
                    'underflow',
                    f'Underflow: {other} is too small for {self.human_format}'
                )
                # Either sticky or ignored, so we need to round properly

            return self._create_same(retval.value, internal=True)
        else:
            return NotImplemented

    # Multiplication

    def __imul__(self, other) -> Self:

        def implementation(val: int, fract: int) -> None:
            # Multiply bits and shift accordingly

            # a / 2 ** N * b / 2 ** M = x / 2 ** N
            # a * b / 2 ** (N + M) = x / 2 ** N
            # x = ab / 2 ** M

            self._clip(shift_round(self.value * val, fract))

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.integer)):
            # Cast to int because NumPy integers are limited.
            # Also optimize by avoiding shift_round.
            self._clip(self.value * int(other))
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                self *= mpmath.mpmathify(other)
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other) and self.value != 0:
                trigger_error(
                    'overflow',
                    f'Overflow: operation on {self.human_format} and {other}'
                )
                self.value = self._max_val if (other > 0) == (self.value > 0) else self._min_val
            elif not mpmath.isfinite(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = 0
            elif self.value and other:  # Avoid zeros
                # Limit calculation - same concept as __iadd__, different calculation:
                #
                # The overflow limit is |self * other| <= 2 ** integer_bits.
                # We choose the minimal value for |self|, which is 2 ** -fraction_bits.
                # We get 2 ** -fraction_bits * |other| <= 2 ** integer_bits,
                # |other| <= 2 ** (fraction_bits + integer_bits).
                #
                # The underflow limit is |self * other| >= 2 ** -(fraction_bits + 1)
                # (with the +1 being for rounding halves).
                # We choose the maximal value for |self|, which is 2 ** integer_bits.
                # Now we get 2 ** integer_bits * |other| >= 2 ** -(fraction_bits + 1):
                # |other| >= 2 ** -(fraction_bits + integer_bits + 1).
                #
                # Finally, our limits are
                # 2 ** -(fraction_bits + integer_bits + 1) <= |other| <= 2 ** (fraction_bits + integer_bits).
                # Using frexp, we get -fraction_bits - integer_bits - 1 <= exponent <= fraction_bits + integer_bits

                mantissa, exp, e = semi_fixed(other)

                if e < -self.fraction_bits - self.integer_bits - 1:
                    trigger_error(
                        'underflow',
                        f'Underflow: {other} is too small for {self.human_format}'
                    )
                    # Silent underflow
                    sign = mpmath.sign(self.value) * mpmath.sign(other)
                    self.value = 0
                    self._handle_underflow_rounding(sign)
                elif e > self.fraction_bits + self.integer_bits:
                    trigger_error(
                        'overflow',
                        f'Overflow: {other} is too big for {self.human_format}'
                    )
                    # Silent overflow
                    self.value = self._max_val              \
                        if (self.value >= 0) == (other >= 0)\
                        else self._min_val
                else:
                    # Calculate like in fixed
                    implementation(mantissa, exp)
            else:
                self.value = 0
        else:
            return NotImplemented

        return self

    def __mul__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__imul__(other)

    def __rmul__(self, other) -> Self:
        if isinstance(other, Fixed):
            return NotImplemented

        return self * other

    # Division

    def __itruediv__(self, other) -> Self:
        return self._div(other)

    def __truediv__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__itruediv__(other)

    def __rtruediv__(self, other) -> Self:
        return self._reverse_div(other)

    # Floor division (//)

    def __ifloordiv__(self, other) -> Self:
        return self._div(
            other,
            rounded_bits=self.fraction_bits,
            rounding=FixedRounding.FLOOR,
            check_underflow=False
        )

    def __floordiv__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__ifloordiv__(other)

    def __rfloordiv__(self, other) -> Self:
        return self._reverse_div(
            other,
            rounded_bits=self.fraction_bits,
            rounding=FixedRounding.FLOOR,
            check_underflow=False
        )

    # Modulo

    def __imod__(self, other) -> Self:
        # a % b = a - modulo_round(a / b) * b

        if other == 0:
            trigger_error('undefined', 'Divide by 0')
            # Letting the error occur in _div will result in a - 0 * 0 = a
            self.value = 0
            return self

        if isinstance(other, (float, numpy.floating, mpmath.mpf)):
            if not mpmath.isfinite(other):
                # x % inf = x - x / inf * inf = x - 0 * inf = x - nan = nan
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = 0
                return self

            _, e = (mpmath.frexp if isinstance(other, mpmath.mpf) else numpy.frexp)(other)
            e -= 1
            if e < -self.fraction_bits - 1:
                # |self % other| < |other| by definition.
                # If |other| < 2 ** -fraction_bits, then it's an underflow.
                # However, we can't calculate the exact result - so it's undefined.
                trigger_error(
                    'undefined',
                    f'Undefined: {other} is too small for {self.human_format}, '
                    "and can't be handled by __imod__"
                )
                self.value = 0
                return self
            # elif e > self.integer_bits
            #    0 <= |self / other| < 1
            #    We can use normal division and rounding to determine the result.
            #    Note that |modulo_round(self / other)| = 1 when rounding up/away etc.
            #    These cases will result in overflow and be handled correctly.
            # else normal operation

        reg = (
            self._common_copy(other)
            if isinstance(other, Fixed)
            else self
        )._higher_precision()._higher_precision()  # Double increase - two operations
        if reg._div(
            other,
            rounded_bits=reg.fraction_bits,
            rounding=get_fixed_state().modulo_rounding,
            check_underflow=False
        ) is NotImplemented:
            return NotImplemented

        self -= reg * other

        return self

    def __mod__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__imod__(other)

    def __rmod__(self, other) -> Self:
        if isinstance(other, Fixed):
            return NotImplemented

        if self.value == 0:
            trigger_error('undefined', 'Divide by 0')
            return self._create_same()

        rounding = get_fixed_state().modulo_rounding

        higher = promote(self)

        if isinstance(other, int):
            # Figure how many bits are required to represent other
            if other.bit_length() > self.integer_bits:
                higher = promote(
                    Fixed(
                        fraction_bits=self.fraction_bits,
                        integer_bits=other.bit_length(),
                        sign=self.sign or other < 0
                    )
                )
        elif isinstance(other, numpy.integer):
            # Similar to int
            if numpy.iinfo(other).bits > self.integer_bits:
                higher = promote(
                    Fixed(
                        fraction_bits=self.fraction_bits,
                        integer_bits=numpy.iinfo(other).bits,
                        sign=self.sign or other < 0
                    )
                )
        elif isinstance(other, (float, numpy.floating, mpmath.mpf)):
            if other == 0:
                return self._create_same()

            if not mpmath.isfinite(other):
                # inf % x = inf - inf / x * inf = inf - inf = nan
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                return self._create_same()

            _, e = (mpmath.frexp if isinstance(other, mpmath.mpf) else numpy.frexp)(other)
            e -= 1
            if e < -self.fraction_bits - 1:
                # |other % self| <= |self|.
                # If |other| < 2 ** -fraction_bits, then it's an underflow.

                trigger_error(
                    'underflow',
                    f'Underflow: {other} is too small for {self.human_format}'
                )

                # The rounding mode determines whether the division result is 1, 0 or -1.
                # Truncation and nearest rounding will always return 0.
                # if signs are equal:
                #   other - modulo_round(|other| / |self|) * self
                #   modulo_round(|other| / |self|) will return 0 when rounding down.
                #   Otherwise it's 1.
                #   And then it's other - 0 or other - 1 * self, so 0 or -self.
                # if signs are unequal:
                #   other - modulo_round(-|other| / |self|) * self
                #   modulo_round(-|other| / |self|) will return 0 when rounding up.
                #   Otherwise it's 0.
                #   And then it's other + 1 * self or other - 0, so self or 0.

                if rounding in (
                        FixedRounding.TRUNC,
                        FixedRounding.ROUND_HALF_DOWN,
                        FixedRounding.ROUND_HALF_UP,
                        FixedRounding.ROUND_HALF_TO_ZERO,
                        FixedRounding.ROUND_HALF_AWAY,
                        FixedRounding.ROUND_HALF_TO_EVEN,
                        FixedRounding.ROUND_HALF_TO_ODD
                ):
                    # other / self is rounded to 0
                    mod_round = 0
                elif mpmath.sign(self.value) == mpmath.sign(other):
                    # Positive result
                    if rounding == FixedRounding.FLOOR:
                        # other / self is rounded down to 0
                        mod_round = 0
                    else:
                        # other / self is rounded up to 1
                        mod_round = 1
                else:
                    # Negative result
                    if rounding == FixedRounding.CEIL:
                        # other / self is rounded up to 0
                        mod_round = 0
                    else:
                        # other / self is rounded down to -1
                        mod_round = -1

                # return other - modulo_round(|other| / |self|) * self
                result = self._higher_precision()
                result *= -mod_round
                result._handle_underflow_rounding(other)
                return self._create_same(result, internal=False)
            elif e > 2 * self.integer_bits:
                # Overflow can't happen, because |other % self| <= |self|.
                # However, division might still overflow.
                # The calculation is outside of the fixed-point's implementation capabilities
                # (will require absurd amounts of bits, e.g. 2048 for double), and therefore,
                # this is an undefined operation.
                trigger_error(
                    'undefined',
                    f'Undefined: {other} is too big for {self.human_format}, '
                    "and can't be handled by __rmod__"
                )
                return self._create_same()
            # else normal operation

        reg = higher(self)._higher_precision()
        reg = reg._reverse_div(
            other,
            rounded_bits=reg.fraction_bits,
            rounding=rounding,
            check_underflow=False
        )
        if reg is NotImplemented:
            return NotImplemented

        return self._create_same(other - reg * self, internal=False)

    # divmod

    def __divmod__(self, other) -> tuple:
        # a % b = a - modulo_round(a / b) * b
        # return modulo_round(a / b), a % b

        def ret_t(x=0):
            return self._create_common(other, x)        \
                if isinstance(other, Fixed)             \
                else self._create_same(x, internal=False)

        if other == 0:
            trigger_error('undefined', 'Divide by 0')
            # Letting the error occur in _div will result in a - 0 * 0 = a
            return ret_t(), ret_t()

        rounding = get_fixed_state().modulo_rounding

        if isinstance(other, (float, numpy.floating, mpmath.mpf)):
            # See __imod__

            if not mpmath.isfinite(other):
                # x % inf = x - x / inf * inf = x - 0 * inf = x - nan = nan
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                return self._create_same(), self._create_same()

            _, e = (mpmath.frexp if isinstance(other, mpmath.mpf) else numpy.frexp)(other)
            e -= 1
            if e < -self.fraction_bits - 1:
                trigger_error(
                    'undefined',
                    f'Undefined: {other} is too small for {self.human_format}, '
                    "and can't be handled by __divmod__"
                )
                # Calculate division result (would probably cause overflow)
                ret = self._create_copy()
                ret._div(
                    other,
                    rounded_bits=self.fraction_bits,
                    rounding=rounding,
                    check_underflow=False
                )
                return ret, self._create_same()

        reg = (
            self._common_copy(other)
            if isinstance(other, Fixed)
            else self
        )._higher_precision()._higher_precision()
        if reg._div(
            other,
            rounded_bits=reg.fraction_bits,
            rounding=rounding,
            check_underflow=False
        ) is NotImplemented:
            return NotImplemented

        return ret_t(reg), ret_t(self - reg * other)

    def __rdivmod__(self, other) -> tuple:
        # a % b = a - modulo_round(a / b) * b
        # return modulo_round(a / b), a % b

        if isinstance(other, Fixed):
            return NotImplemented

        if self.value == 0:
            trigger_error('undefined', 'Divide by 0')
            return self._create_same(), self._create_same()

        rounding = get_fixed_state().modulo_rounding

        higher = promote(self)

        if isinstance(other, int):
            # Figure how many bits are required to represent other
            if other.bit_length() > self.integer_bits:
                higher = promote(
                    Fixed(
                        fraction_bits=self.fraction_bits,
                        integer_bits=other.bit_length(),
                        sign=self.sign or other < 0
                    )
                )
        elif isinstance(other, numpy.integer):
            # Similar to int
            if numpy.iinfo(other).bits > self.integer_bits:
                higher = promote(
                    Fixed(
                        fraction_bits=self.fraction_bits,
                        integer_bits=numpy.iinfo(other).bits,
                        sign=self.sign or other < 0
                    )
                )
        elif isinstance(other, (float, numpy.floating, mpmath.mpf)):
            if other == 0:
                return self._create_same(), self._create_same()

            if not mpmath.isfinite(other):
                # inf % x = inf - inf / x * inf = inf - inf = nan
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                return self._reverse_div(
                    other,
                    rounded_bits=self.fraction_bits,
                    rounding=rounding,
                    check_underflow=False
                ), self._create_same()

            _, e = (mpmath.frexp if isinstance(other, mpmath.mpf) else numpy.frexp)(other)
            e -= 1
            if e < -self.fraction_bits - 1:
                # See __rmod__

                trigger_error(
                    'underflow',
                    f'Underflow: {other} is too small for {self.human_format}'
                )

                if rounding in (
                        FixedRounding.TRUNC,
                        FixedRounding.ROUND_HALF_DOWN,
                        FixedRounding.ROUND_HALF_UP,
                        FixedRounding.ROUND_HALF_TO_ZERO,
                        FixedRounding.ROUND_HALF_AWAY,
                        FixedRounding.ROUND_HALF_TO_EVEN,
                        FixedRounding.ROUND_HALF_TO_ODD
                ):
                    # other / self is rounded to 0
                    mod_round = 0
                elif mpmath.sign(self.value) == mpmath.sign(other):
                    # Positive result
                    if rounding == FixedRounding.FLOOR:
                        # other / self is rounded down to 0
                        mod_round = 0
                    else:
                        # other / self is rounded up to 1
                        mod_round = 1
                else:
                    # Negative result
                    if rounding == FixedRounding.CEIL:
                        # other / self is rounded up to 0
                        mod_round = 0
                    else:
                        # other / self is rounded down to -1
                        mod_round = -1

                # return modulo_round(other / self), other - modulo_round(other / self) * self
                result = self._higher_precision()
                result *= -mod_round
                result._handle_underflow_rounding(other)
                return self._create_same(mod_round, internal=False), \
                    self._create_same(result, internal=False)
            elif e > 2 * self.integer_bits:
                # See __rmod__
                trigger_error(
                    'undefined',
                    f'Undefined: {other} is too big for {self.human_format}, '
                    "and can't be handled by __rdivmod__"
                )
                return self._reverse_div(
                    other,
                    rounded_bits=self.fraction_bits,
                    rounding=rounding,
                    check_underflow=False
                ), self._create_same()
            # else normal operation

        reg = higher(self)._higher_precision()
        reg = reg._reverse_div(
            other,
            rounded_bits=reg.fraction_bits,
            rounding=rounding,
            check_underflow=False
        )
        if reg is NotImplemented:
            return NotImplemented

        mod = other - reg * self
        if mod == self:
            mod = 0

        return self._create_same(reg, internal=False), self._create_same(mod, internal=False)

    # Shifts (multiply/divide by a power of 2)

    def __ilshift__(self, other) -> Self:
        if not isinstance(other, (int, numpy.integer)):
            return NotImplemented

        self._clip(shift_round(self.value, -int(other)))
        return self

    def __lshift__(self, other) -> Self:
        result = self._create_copy()
        return result.__ilshift__(other)

    def __irshift__(self, other) -> Self:
        if not isinstance(other, (int, numpy.integer)):
            return NotImplemented

        self._clip(shift_round(self.value, int(other)))
        return self

    def __rshift__(self, other) -> Self:
        result = self._create_copy()
        return result.__irshift__(other)

    # Bitwise

    def __iand__(self, other) -> Self:
        def implementation(val: int, fract: int):
            self._clip(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a & b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.integer)):
            implementation(int(other), 0)
        else:
            return NotImplemented

        return self

    def __and__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__iand__(other)

    def __rand__(self, other) -> Self:
        if isinstance(other, Fixed):
            return NotImplemented

        return self & other

    def __ior__(self, other) -> Self:
        def implementation(val: int, fract: int):
            self._clip(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a | b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.integer)):
            implementation(int(other), 0)
        else:
            return NotImplemented

        return self

    def __or__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__ior__(other)

    def __ror__(self, other) -> Self:
        if isinstance(other, Fixed):
            return NotImplemented

        return self | other

    def __ixor__(self, other) -> Self:
        def implementation(val: int, fract: int):
            self._clip(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a ^ b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.integer)):
            implementation(int(other), 0)
        else:
            return NotImplemented

        return self

    def __xor__(self, other) -> Self:
        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__ixor__(other)

    def __rxor__(self, other) -> Self:
        if isinstance(other, Fixed):
            return NotImplemented

        return self ^ other

    # Comparisons

    def cmp(self, other) -> int | float:
        """Compares Fixed and another value via subtraction

        Args:
            other (int, float, Fixed, NumPy int/float, mpmath.mpf): Value to compare against

        Returns:
            int: Comparison result.
                 Positive means self > other.
                 0 means self == other.
                 Negative means self < other.
                 NaN means other is Nan.
        """

        if isinstance(other, Fixed):
            return self._common_precision(other.value, other.fraction_bits, lambda a, b: a - b, False)
        elif isinstance(other, (bool, int, numpy.integer)):
            return self.value - (int(other) << self.fraction_bits)
        elif isinstance(other, (float, numpy.floating)):
            return self.cmp(mpmath.mpmathify(other))
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                return -int(mpmath.sign(other))
            elif mpmath.isnan(other):
                return math.nan

            if other == 0:
                return self.value

            mantissa, exp, e = semi_fixed(other)

            if e >= self.sign + self.integer_bits:
                # other is outside self's range
                return -mpmath.sign(other)
            elif e >= -self.fraction_bits:
                # Treat it like a fixed
                return self._common_precision(mantissa, exp, lambda a, b: a - b, False)
            else:
                # Other is smaller than self.epsilon.
                # If self < 0, then other > self.
                # If self > 0, then other < self.
                # If self = 0, then compare other with 0.
                return self.value if self.value else -mpmath.sign(other)
        else:
            return NotImplemented

    def __eq__(self, other) -> bool:
        return self.cmp(other) == 0

    def __ne__(self, other) -> bool:
        return self.cmp(other) != 0

    def __lt__(self, other) -> bool:
        return self.cmp(other) < 0

    def __le__(self, other) -> bool:
        return self.cmp(other) <= 0

    def __gt__(self, other) -> bool:
        return self.cmp(other) > 0

    def __ge__(self, other) -> bool:
        return self.cmp(other) >= 0

    # NumPy support (avoid conversions to numpy.floating)

    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        ops = {
            numpy.add: 'add__',
            numpy.subtract: 'sub__',
            numpy.multiply: 'mul__',
            numpy.divide: 'truediv__',
            numpy.floor_divide: 'floordiv__',
            numpy.mod: 'mod__',
            numpy.divmod: 'divmod__',
            numpy.left_shift: 'lshift__',
            numpy.right_shift: 'rshift__',
            numpy.bitwise_and: 'and__',
            numpy.bitwise_or: 'or__',
            numpy.bitwise_xor: 'xor__',
            numpy.equal: 'eq__',
            numpy.not_equal: 'ne__',
            numpy.less: 'lt__',
            numpy.less_equal: 'le__',
            numpy.greater: 'gt__',
            numpy.greater_equal: 'ge__',
        }

        if method == '__call__' and ufunc in ops:
            name = ops[ufunc]

            if isinstance(args[0], Fixed):
                return getattr(Fixed, '__' + name)(*args)
            elif not 'shift' in name:
                return getattr(Fixed, '__r' + name)(*(args[::-1]))

        return NotImplemented

# Aliases


def create_alias(f: int, i: int, s: int):
    """Creates a fixed-point alias

    Args:
        f (int): Fraction bits
        i (int): Integer bits
        s (int): Signedness

    Returns:
        Alias
    """

    class Alias(Fixed):
        def __init__(self, value=None, internal: bool = False):
            Fixed.__init__(self, value, f, i, s, internal)

    return Alias


# Q7 (Q1.7) alias (1 sign bit, 0 integer bits, 7 fraction bits)
q7 = create_alias(7, 0, 1)

# Q15 (Q1.15) alias (1 sign bit, 0 integer bits, 15 fraction bits)
q15 = create_alias(15, 0, 1)

# Q31 (Q1.31) alias (1 sign bit, 0 integer bits, 31 fraction bits)
q31 = create_alias(31, 0, 1)

# Q9.7 alias (1 sign bit, 8 integer bits, 7 fraction bits)
q9_7 = create_alias(7, 8, 1)

# Q17.15 alias (1 sign bit, 16 integer bits, 15 fraction bits)
q17_15 = create_alias(15, 16, 1)

# Q33.31 alias (1 sign bit, 32 integer bits, 31 fraction bits)
q33_31 = create_alias(31, 32, 1)


def fixed_alias(value: Fixed) -> type:
    """Create a type alias from a fixed-point value

    Args:
        value (Fixed): Value to create an alias of

    Returns:
        type: Fixed-point alias
    """

    return create_alias(value.fraction_bits, value.integer_bits, value.sign)


def promote_sum(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision for multiple summations

    Args:
        value (type | Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type
    """

    if isinstance(value, type):
        value = value()

    return create_alias(
        value.fraction_bits,
        2 * value.integer_bits + value.fraction_bits + value.sign,
        True
    )


def promote_prod(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision for product operations (e.g. convolution)

    Args:
        value (type | Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type
    """

    if isinstance(value, type):
        value = value()

    # Promote for summation and multiply everything by 2
    return create_alias(
        2 * value.fraction_bits,
        2 * (2 * value.integer_bits + value.fraction_bits + value.sign) + 1,
        True
    )


def promote(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision

    Args:
        value (type | Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type

    Note: the returned type is suitable for all operations, assuming only 1 operation is performed.
    It guarantees that there will be no over/underflow when operating on the original precision.
    """

    if isinstance(value, type):
        value = value()

    return create_alias(
        2 * (value.fraction_bits + value.integer_bits + value.sign),
        2 * (value.fraction_bits + value.integer_bits + value.sign),
        True
    )
