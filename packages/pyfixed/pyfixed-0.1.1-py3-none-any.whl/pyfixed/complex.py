"""Internal complex fixed-point implementation module

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

import math
import mpmath
import numpy
from typing_extensions import Self
import warnings

from pyfixed.fixed import *


class PartialOrdering(enum.Enum):
    """Partial ordering enum, similar to C++'s:
       https://en.cppreference.com/w/cpp/utility/compare/partial_ordering
    """

    LESS = enum.auto()
    EQUAL = enum.auto()
    GREATER = enum.auto()
    UNORDERED = enum.auto()


class ComplexFixed:
    """Complex fixed-point
    """

    @property
    def fraction_bits(self) -> int:
        return self.real.fraction_bits

    @property
    def integer_bits(self) -> int:
        return self.real.integer_bits

    @property
    def sign(self) -> int:
        return self.real.sign

    @property
    def _min_val(self):
        return self.real._min_val

    @property
    def _max_val(self):
        return self.real._max_val

    @property
    def epsilon(self):
        return self.real.epsilon

    @property
    def half(self):
        return self.real.half

    @property
    def one(self):
        return self.real.one

    @property
    def human_format(self) -> str:
        return self.real.human_format

    def _create_same(self, *args, **kwargs) -> Self:
        """Creates a complex fixed-point number of the same configuration as self

        Args:
            Same as ComplexFixed.__init__

        Returns:
            ComplexFixed: New complex fixed-point number
        """

        return ComplexFixed(
            *args,
            **kwargs,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign
        )

    def _create_copy(self) -> Self:
        """Creates a copy of this number

        Returns:
            ComplexFixed: Copy
        """

        return self._create_same(self)

    def _create_common(self, other: Fixed | Self, *args, **kwargs) -> Self:
        """Creates a number in a common precision

        Args:
            other (Fixed, ComplexFixed): Other fixed
            ...: Arguments for ComplexFixed.__init__

        Returns:
            ComplexFixed: Common precision number
        """

        return ComplexFixed(
            *args,
            **kwargs,
            fraction_bits=max(self.fraction_bits, other.fraction_bits),
            integer_bits=max(self.integer_bits, other.integer_bits),
            sign=self.sign or other.sign
        )

    def _common_copy(self, other: Fixed | Self) -> Self:
        """Creates a copy of self in a common precision

        Args:
            other (Fixed, ComplexFixed): Other fixed

        Returns:
            ComplexFixed: Common precision copy
        """

        return self._create_common(other, self)

    def _higher_precision(self) -> Self:
        """Creates a higher precision copy of this number

        Returns:
            ComplexFixed: Higher precision copy
        """

        r = promote(self.real)()

        return ComplexFixed(
            self,
            fraction_bits=r.fraction_bits,
            integer_bits=r.integer_bits,
            sign=True
        )

    @staticmethod
    def _is_real_type(x) -> bool:
        """Checks if x's type is real

        Args:
            x (any): Number to check the type of

        Returns:
            bool: Whether x is real
        """

        return isinstance(
            x,
            (
                bool,
                int,
                float,
                numpy.integer,
                numpy.floating,
                mpmath.mpf,
                Fixed,
            )
        )

    @staticmethod
    def _is_complex_type(x) -> bool:
        """Checks if x's type is complex

        Args:
            x (any): Number to check the type of

        Returns:
            bool: Whether x is complex
        """

        return isinstance(
            x,
            (
                complex,
                numpy.complexfloating,
                mpmath.mpc,
                ComplexFixed,
            )
        )

    def _isnan(self, x) -> bool:
        """Checks if x is NaN and triggers an error if so

        Args:
            x (any): Number to check

        Returns:
            bool: x != x
        """

        res = isinstance(
            x,
            (
                float,
                complex,
                numpy.floating,
                numpy.complexfloating,
                mpmath.mpf,
                mpmath.mpc
            )
        ) and mpmath.isnan(x)

        if res:
            trigger_error(
                'undefined',
                f'Undefined: operation on {self.human_format} and {x}'
            )

        return res

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
            ComplexFixed: result (self or NotImplemented)
        """

        if self._isnan(other):
            self.real.value = 0
            self.imag.value = 0
        elif ComplexFixed._is_real_type(other):
            self.real._div(other, rounded_bits, rounding, check_underflow)
            self.imag._div(other, rounded_bits, rounding, check_underflow)
        elif isinstance(other, ComplexFixed):
            # (a + bi) / (c + di) = (a + bi)(c - di) / (c ** 2 + d ** 2)
            # Precision is increased to avoid over/underflow

            a = self.real._higher_precision()._higher_precision()
            b = self.imag._higher_precision()._higher_precision()
            c = other.real._higher_precision()._higher_precision()
            d = other.imag._higher_precision()._higher_precision()

            mul_r = a * c + b * d
            mul_i = b * c - a * d

            if rounded_bits:
                rounded_bits += mul_r.fraction_bits - self.fraction_bits

            c_d = c * c + d * d
            self.real._clip(
                shift_round(
                    mul_r._div(
                        c_d,
                        rounded_bits,
                        rounding,
                        check_underflow
                    ).value,
                    mul_r.fraction_bits - self.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
            self.imag._clip(
                shift_round(
                    mul_i._div(
                        c_d,
                        rounded_bits,
                        rounding,
                        check_underflow
                    ).value,
                    mul_i.fraction_bits - self.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
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
            ComplexFixed: result (or NotImplemented)
        """

        if ComplexFixed._is_complex_type(other):
            return NotImplemented

        c = self.real._higher_precision()._higher_precision()
        d = self.imag._higher_precision()._higher_precision()
        c_d = c * c + d * d

        if ComplexFixed._is_real_type(other):
            # a / (c + di) = a * (c - di) / (c ** 2 + d ** 2)
            mul_r = c * other
            mul_i = -d * other

            if rounded_bits:
                rounded_bits += mul_r.fraction_bits - self.fraction_bits

            result = self._create_common(other)\
                if isinstance(other, Fixed)    \
                else self._create_same()

            result.real._clip(
                shift_round(
                    mul_r._div(c_d, rounded_bits, rounding, check_underflow).value,
                    mul_r.fraction_bits - result.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
            result.imag._clip(
                shift_round(
                    mul_i._div(c_d, rounded_bits, rounding, check_underflow).value,
                    mul_i.fraction_bits - result.fraction_bits,
                    rounding,
                    check_underflow
                )
            )

            return result
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
            Fixed |
            Self
        = None,
        real:
            int |
            float |
            numpy.integer |
            numpy.floating |
            mpmath.mpf |
            Fixed
        = None,
        imag:
            int |
            float |
            numpy.integer |
            numpy.floating |
            mpmath.mpf |
            Fixed
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        internal=False,
    ):
        """Initializes a new fixed-point complex number

        Args:
            value (
                int,
                float,
                complex,
                numpy.integer,
                numpy.floating,
                numpy.complexfloating,
                mpmath.mpf,
                mpmath.mpc,
                Fixed,
                Self,
                optional
            ): Initial value. Defaults to None.
               Mutually exclusive with 'real' and 'imag'.
            real (
                int,
                float,
                numpy.integer,
                numpy.floating,
                mpmath.mpf,
                Fixed,
                optional
            ): Initial real value. Defaults to None.
               Mutually exclusive with 'value'.
            imag (
                int,
                float,
                numpy.integer,
                numpy.floating,
                mpmath.mpf,
                Fixed,
                optional
            ): Initial imaginary value. Defaults to None.
               Mutually exclusive with 'value'.
            fraction_bits (int, optional): Number of fraction bits. Defaults to 52.
            integer_bits (int, optional): Number of integer bits. Defaults to 11.
            sign (bool, optional): Signedness. Defaults to True.
            internal (bool, optional): Directly store the initial value(s). Defaults to False.
        """

        if value is not None and (real is not None or imag is not None):
            raise ValueError("'value' is mutually exclusive with 'real' and 'imag'")

        if ComplexFixed._is_complex_type(real) or ComplexFixed._is_complex_type(imag):
            raise ValueError("'real' and 'imag' must be of real types (or None)")

        # Deduce configuration
        if isinstance(value, (Fixed, ComplexFixed)):
            if fraction_bits is None:
                fraction_bits = value.fraction_bits
            if integer_bits is None:
                integer_bits = value.integer_bits
            if sign is None:
                sign = value.sign
        elif isinstance(real, Fixed) or isinstance(imag, Fixed):
            r_fixed = real if isinstance(real, Fixed) else imag
            i_fixed = imag if isinstance(imag, Fixed) else real

            if fraction_bits is None:
                fraction_bits = max(r_fixed.fraction_bits, i_fixed.fraction_bits)
            if integer_bits is None:
                integer_bits = max(r_fixed.integer_bits, i_fixed.integer_bits)
            if sign is None:
                sign = r_fixed.sign or i_fixed.sign
        else:
            if fraction_bits is None:
                fraction_bits = 52
            if integer_bits is None:
                integer_bits = 11
            if sign is None:
                sign = True

        fixed_type = create_alias(fraction_bits, integer_bits, sign)

        if value is not None:
            if ComplexFixed._is_real_type(value):
                init_real = value
                init_imag = 0
            elif ComplexFixed._is_complex_type(value):
                init_real = value.real
                init_imag = value.imag
            else:
                raise ValueError(f'Unrecognized type {type(value)}')
        else:
            init_real = real if real is not None else 0
            init_imag = imag if imag is not None else 0

        self.real = fixed_type(init_real, internal=internal)
        self.imag = fixed_type(init_imag, internal=internal)

    # Conversions

    def __bool__(self) -> bool:
        return bool(self.real) or bool(self.imag)

    def __int__(self) -> int:
        return int(self.real)

    def __float__(self) -> float:
        return float(self.real)

    def __complex__(self) -> complex:
        return complex(float(self.real), float(self.imag))

    def __repr__(self) -> str:
        return f'Complex{self.human_format}({str(self)})'

    def __str__(self) -> str:
        imag_sign = self.imag.value < 0
        return f'{str(self.real)} {"-" if imag_sign else "+"} 1j * {str(self.imag)[imag_sign:]}'

    def __format__(self) -> str:
        return str(self)

    def __bytes__(self) -> bytes:
        return bytes(self.real) + bytes(self.imag)

    def __array__(self, dtype_meta=numpy.dtypes.Complex128DType, copy: bool = True) -> numpy.ndarray:
        """Converts to NumPy

        Args:
            dtype_meta (numpy._DTypeMeta, optional): dtype meta from NumPy.
                                                     Defaults to complex double.
            copy (bool, optional) Create a copy.
                                  Defaults to True.

        Raises:
            TypeError: copy=False

        Returns:
            numpy.ndarray: Converted value
        """

        dtype = dtype_meta.type

        if copy is False:
            raise TypeError(f'Casting ComplexFixed to {dtype} requires creating a copy')

        if issubclass(dtype, numpy.complexfloating):
            return numpy.array(dtype(self.real) + 1j * dtype(self.imag))
        else:
            warnings.warn(
                numpy.exceptions.ComplexWarning(
                    'Casting complex values to real discards the imaginary part'
                ),
                stacklevel=2
            )
            return numpy.array(dtype(self.real))

    def mpmath(self) -> mpmath.mpc:
        """Converts to mpmath.mpc

        Returns:
            mpmath.mpc: Converted value
        """

        return mpmath.mpc(self.real.mpmath(), self.imag.mpmath())

    # Unary operators

    def __pos__(self) -> Self:
        return self._create_copy()

    def __neg__(self) -> Self:
        return self._create_same(real=-self.real, imag=-self.imag)

    # Rounding

    def __floor__(self) -> tuple:
        return self.real.__floor__(), self.imag.__floor__()

    def __ceil__(self) -> tuple:
        return self.real.__ceil__(), self.imag.__ceil__()

    def __trunc__(self) -> tuple:
        return self.real.__trunc__(), self.imag.__trunc__()

    def __round__(self, ndigits=None) -> tuple | Self:
        if ndigits is None:
            return round(self.real), round(self.imag)

        return self._create_same(real=round(self.real, ndigits), imag=round(self.imag, ndigits))

    # Binary operators

    # Addition

    def __iadd__(self, other) -> Self:
        if ComplexFixed._is_real_type(other):
            self.real += other
        elif isinstance(other, ComplexFixed):
            self.real += other.real
            self.imag += other.imag
        else:
            return NotImplemented

        return self

    def __add__(self, other) -> Self:
        result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
        return result.__iadd__(other)

    def __radd__(self, other) -> Self:
        if isinstance(other, ComplexFixed):
            return NotImplemented

        return self.__add__(other)

    # Subtraction

    def __isub__(self, other) -> Self:
        if ComplexFixed._is_real_type(other):
            self.real -= other
        elif isinstance(other, ComplexFixed):
            self.real -= other.real
            self.imag -= other.imag
        else:
            return NotImplemented

        return self

    def __sub__(self, other) -> Self:
        result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
        return result.__isub__(other)

    def __rsub__(self, other) -> Self:
        if ComplexFixed._is_complex_type(other):
            return NotImplemented

        r = other - self.real
        i = -(self.imag._higher_precision())

        return self._create_common(other, real=r, imag=i)\
            if is_fixed_point(other)                     \
            else self._create_same(real=r, imag=i)

    # Multiplication

    def __imul__(self, other) -> Self:
        if ComplexFixed._is_real_type(other):
            self.real *= other
            self.imag *= other
        elif isinstance(other, ComplexFixed):
            result = self * other
            self.real = result.real
            self.imag = result.imag
        else:
            return NotImplemented

        return self

    def __mul__(self, other) -> Self:
        other_fixed = is_fixed_point(other)

        if ComplexFixed._is_real_type(other):
            result = self._common_copy(other) if other_fixed else self._create_copy()
            return result.__imul__(other)
        elif isinstance(other, ComplexFixed):
            # (a + bi)(c + di) = ac - bd + i * (bc + ad)
            # Increase precision to avoid overflow errors

            a = self.real._higher_precision()._higher_precision()
            b = self.imag._higher_precision()._higher_precision()
            # Casting c and d to higher precision is required
            # in case other is more precise than self
            c = other.real._higher_precision()._higher_precision()
            d = other.imag._higher_precision()._higher_precision()

            result_real = a * c - b * d
            result_imag = b * c + a * d

            return self._create_common(
                other,
                real=result_real,
                imag=result_imag
            )
        else:
            return NotImplemented

    def __rmul__(self, other) -> Self:
        if isinstance(other, ComplexFixed):
            return NotImplemented

        return self.__mul__(other)

    # Division

    def __itruediv__(self, other) -> Self:
        return self._div(other)

    def __truediv__(self, other) -> Self:
        result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
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
        # See Fixed.__imod__

        if ComplexFixed._is_real_type(other):
            self.real %= other
            self.imag %= other
        elif isinstance(other, ComplexFixed):
            if not other.real.value and not other.imag.value:
                trigger_error('undefined', 'Divide by 0')
                self.real.value = 0
                self.imag.value = 0
                return self

            reg = self._common_copy(other)._higher_precision()._higher_precision()
            reg._div(
                other,
                rounded_bits=reg.fraction_bits,
                rounding=get_fixed_state().modulo_rounding,
                check_underflow=False
            )

            self -= reg * other
        else:
            return NotImplemented

        return self

    def __mod__(self, other) -> Self:
        result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
        return result.__imod__(other)

    def __rmod__(self, other) -> Self:
        # See Fixed.__rmod__

        if ComplexFixed._is_complex_type(other) or isinstance(
            other,
            (
                float,
                numpy.floating,
                mpmath.mpf
            )
        ):
            return NotImplemented

        def ret_t(*args, **kwargs):
            return self._create_common(other, *args, **kwargs)        \
                if is_fixed_point(other)                              \
                else self._create_same(*args, **kwargs, internal=False)

        rounding = get_fixed_state().modulo_rounding

        if ComplexFixed._is_real_type(other):
            if not self.real.value and not self.imag.value:
                trigger_error('undefined', 'Divide by 0')
                return ret_t()

            reg = ret_t(self)._higher_precision()._higher_precision()
            reg = reg._reverse_div(
                other,
                rounded_bits=reg.fraction_bits,
                rounding=get_fixed_state().modulo_rounding,
                check_underflow=False
            )

            return ret_t(other - reg * self)
        else:
            return NotImplemented

    # divmod

    def __divmod__(self, other) -> tuple:
        # See Fixed.__divmod__

        def ret_t(*args, **kwargs):
            return self._create_common(other, *args, **kwargs)        \
                if is_fixed_point(other)                              \
                else self._create_same(*args, **kwargs, internal=False)

        if ComplexFixed._is_real_type(other):
            r = divmod(self.real, other)
            i = divmod(self.imag, other)
            return ret_t(real=r[0], imag=i[0]), ret_t(real=r[1], imag=i[1])
        elif isinstance(other, ComplexFixed):
            if not other.real.value and not other.imag.value:
                trigger_error('undefined', 'Divide by 0')
                return ret_t(), ret_t()

            reg = self._common_copy(other)._higher_precision()._higher_precision()
            reg._div(
                other,
                rounded_bits=reg.fraction_bits,
                rounding=get_fixed_state().modulo_rounding,
                check_underflow=False
            )

            return ret_t(reg), ret_t(self - reg * other)
        else:
            return NotImplemented

    def __rdivmod__(self, other) -> tuple:
        def ret_t(*args, **kwargs):
            return self._create_common(other, *args, **kwargs)        \
                if is_fixed_point(other)                              \
                else self._create_same(*args, **kwargs, internal=False)

        if ComplexFixed._is_real_type(other) and not isinstance(
            other,
            (
                float,
                numpy.floating,
                mpmath.mpf
            )
        ):
            if not self.real.value and not self.imag.value:
                trigger_error('undefined', 'Divide by 0')
                return ret_t(), ret_t()

            reg = ret_t(self)._higher_precision()._higher_precision()
            reg = reg._reverse_div(
                other,
                rounded_bits=reg.fraction_bits,
                rounding=get_fixed_state().modulo_rounding,
                check_underflow=False
            )

            return ret_t(reg), ret_t(other - reg * self)
        else:
            return NotImplemented

    # Shifts (multiply/divide by a power of 2)

    def __ilshift__(self, other) -> Self:
        self.real <<= other
        self.imag <<= other
        return self

    def __lshift__(self, other) -> Self:
        result = self._create_copy()
        return result.__ilshift__(other)

    def __irshift__(self, other) -> Self:
        self.real >>= other
        self.imag >>= other
        return self

    def __rshift__(self, other) -> Self:
        result = self._create_copy()
        return result.__irshift__(other)

    # Comparisons

    def cmp(self, other) -> PartialOrdering:
        """Compares ComplexFixed and another value

        Args:
            other (any): Value to compare against

        Returns:
            PartialOrdering: Comparison result
        """

        # Compare the components themselves

        if ComplexFixed._is_real_type(other):
            real_cmp = self.real.cmp(other)
            imag_cmp = self.imag.value
        elif ComplexFixed._is_complex_type(other):
            real_cmp = self.real.cmp(other.real)
            imag_cmp = self.imag.cmp(other.imag)
        else:
            return NotImplemented

        # nan == nan returns False
        if (real_cmp != real_cmp) or (imag_cmp != imag_cmp):
            return PartialOrdering.UNORDERED

        # Convert the results to PartialOrdering
        if real_cmp == 0 and imag_cmp == 0:
            return PartialOrdering.EQUAL
        elif real_cmp and imag_cmp:
            return PartialOrdering.UNORDERED
        elif real_cmp:
            return PartialOrdering.GREATER if real_cmp > 0 else PartialOrdering.LESS
        else:  # imag_cmp != 0
            return PartialOrdering.GREATER if imag_cmp > 0 else PartialOrdering.LESS

    def __eq__(self, other) -> bool:
        return self.cmp(other) == PartialOrdering.EQUAL

    def __ne__(self, other) -> bool:
        return self.cmp(other) != PartialOrdering.EQUAL

    def __lt__(self, other) -> bool:
        return self.cmp(other) == PartialOrdering.LESS

    def __le__(self, other) -> bool:
        return self.cmp(other) in (PartialOrdering.LESS, PartialOrdering.EQUAL)

    def __gt__(self, other) -> bool:
        return self.cmp(other) == PartialOrdering.GREATER

    def __ge__(self, other) -> bool:
        return self.cmp(other) in (PartialOrdering.GREATER, PartialOrdering.EQUAL)

    # NumPy support

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

        if method == '__call__':
            if ufunc == numpy.conj:
                return self._create_same(real=self.real, imag=-self.imag)

            if ufunc in ops:
                name = ops[ufunc]

                if isinstance(args[0], ComplexFixed):
                    return getattr(ComplexFixed, '__' + name)(*args)
                elif not 'shift' in name:
                    return getattr(ComplexFixed, '__r' + name)(*(args[::-1]))

        return NotImplemented


def is_fixed_point(x) -> bool:
    """Checks if x is a fixed-point number

    Args:
        x (any): Number to check

    Returns:
        bool: True if x is a fixed-point number (real or complex)
    """

    return isinstance(x, (Fixed, ComplexFixed))
