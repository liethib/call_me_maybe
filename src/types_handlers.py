import re
import numpy as np
from abc import ABC, abstractmethod
from typing import Any


class TypeHandler(ABC):
    @abstractmethod
    def get_valid_tokens(self, vocab: np.ndarray,
                         current_buffer: str,
                         is_last: bool = False) -> np.ndarray:
        pass

    @abstractmethod
    def is_complete(self, current_buffer: str, is_last: bool = False) -> bool:
        pass


class StringHandler(TypeHandler):
    def __init__(self, vocab: np.ndarray) -> None:
        self.non_last_mask = np.char.find(vocab, '"}') == -1
        self.last_mask = np.char.find(vocab, '",') == -1
        self.no_leading_whitespace_mask = np.array(
            [not s[:1].isspace() for s in vocab], 
            dtype=bool
        )

    def get_valid_tokens(self, vocab: np.ndarray,
                         current_buffer: str, is_last: bool = False)\
            -> Any:
        """Returns a mask with available characters,
         depending if it's the last argument or not."""
        mask = self.last_mask if is_last else self.non_last_mask
        if len(current_buffer) < 1:
            return mask & self.no_leading_whitespace_mask

        return mask

    def is_complete(self, current_buffer: str, is_last: bool = False) -> bool:
        """Returns the boolean value whether the state is considered
         complete (usually ends with a terminator such as \", ',' or '}')"""
        if current_buffer.endswith('\\"'):
            return False
        trimmed_buffer = current_buffer.rstrip()
        if is_last:
            return trimmed_buffer.endswith('"') or trimmed_buffer.endswith('"}}')
        return trimmed_buffer.endswith('"') or trimmed_buffer.endswith('",')
            # or trimmed_buffer.endswith('}')


class IntHandler(TypeHandler):
    def __init__(self, vocab: np.ndarray) -> None:
        self.digit_mask = np.array(
            [len(s) > 0 and s.isdigit() for s in vocab])
        self.minus_mask = np.char.equal(vocab, '-')
        self.comma_mask = np.char.equal(vocab, ',')
        self.brace_mask = np.char.equal(vocab, '}')

    def get_valid_tokens(self, vocab: np.ndarray,
                         current_buffer: str,
                         is_last: bool = False) -> np.ndarray:
        """Returns a mask with available characters,
         depending if it's the last argument or not."""
        has_digit = any(c.isdigit() for c in current_buffer)
        terminator = self.brace_mask if is_last else self.comma_mask

        mask = self.digit_mask.copy()
        if not has_digit:
            mask |= self.minus_mask
        if has_digit:
            mask |= terminator
        return mask

    def is_complete(self, current_buffer: str, is_last: bool = False) -> bool:
        """Returns the boolean value whether the state is considered
         complete (usually ends with a terminator such as \", ',' or '}')"""
        return current_buffer.endswith(',') or current_buffer.endswith('}')


class FloatHandler(TypeHandler):
    def __init__(self, vocab: np.ndarray) -> None:
        # pattern = re.compile(r'^[-0-9},.]+$')
        pattern = re.compile(r'^[\sĠ\u2581]*\-?[0-9]*\.?[0-9]*$')
        match = np.vectorize(lambda x: bool(pattern.fullmatch(x)))
        self.base_mask = match(vocab)
        self.base_mask |= np.char.equal(vocab, '}')
        self.comma_mask = self.base_mask | np.char.equal(vocab, ',')

    def get_valid_tokens(self, vocab: np.ndarray,
                         current_buffer: str,
                         is_last: bool = False) -> Any:
        """Returns a mask with available characters,
        depending if it's the last argument or not."""
        if is_last:
            return self.base_mask.copy()
        return self.comma_mask.copy()

    def is_complete(self, current_buffer: str, is_last: bool = False) -> bool:
        """Returns the boolean value whether the state is considered
        complete (usually ends with a terminator such as \", ',' or '}')"""
        return current_buffer.endswith(',') or current_buffer.endswith('}')


class BoolHandler(TypeHandler):
    def __init__(self, vocab: np.ndarray) -> None:
        valid_bools = [
            'true', 'false', 'True', 'False',
            ' true', ' false', 'Ġtrue', 'Ġfalse',
            '}'
        ]
        self.base_mask = np.isin(vocab, valid_bools)
        self.non_last_mask = self.base_mask | np.char.find(vocab, '"}') == -1
        self.last_mask = self.base_mask | np.char.find(vocab, '",') == -1

    def get_valid_tokens(self, vocab: np.ndarray,
                         current_buffer: str,
                         is_last: bool = False) -> Any:
        """Returns a mask with available characters,
        depending if it's the last argument or not."""
        if is_last:
            return self.last_mask
        return self.non_last_mask

    def is_complete(self, current_buffer: str, is_last: bool = False) -> bool:
        """Returns the boolean value whether the state is considered
        complete (usually ends with a terminator such as \", ',' or '}')"""
        # return current_buffer.endswith(',') or current_buffer.endswith('}')
        trimmed_buffer = current_buffer.rstrip()
        if is_last:
            return trimmed_buffer.endswith('"') or trimmed_buffer.endswith('}')
        return trimmed_buffer.endswith('"') or trimmed_buffer.endswith('",')\
            or trimmed_buffer.endswith('}')
