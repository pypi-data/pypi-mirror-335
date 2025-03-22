"""Module providing the matcher class implementing the recursive algorithm."""

import numpy as np


class Matcher:
    """
    The `Matcher` class provides an algorithm for matching rows or columns of
    a matrix based on the values in the matrix. The matching process can be
    controlled by an axis, a limit on the matching value, and a minimum 
    threshold for the values to be considered in the match.
    """

    def __init__(
        self,
        matrix: np.ndarray,
        axis: int,
        limit: bool,
    ):
        """
        Creates a new `Matcher` instance.

        Parameters
        ----------
        matrix : np.ndarray
            The input matrix as a 2D array. Each row 
            can only be matched to one item in the
            column or vice versa.
        axis : int
            For row by row matching, specify as 0. For column
            by column matching, specify as 1. Row by row means
            to loop through each row and find the best value
            of each row based on the maximum.
        limit : bool
            Do not match if the value of the match is the
            minimum (default) / maximum (set minimum to True) in the matrix.
        """
        self.__matrix = matrix
        self.__axis = axis
        self.__limit = limit
        self.__min_value = np.min(matrix)
        self.__matches = np.ones(matrix.shape[axis], dtype=np.int32) * -1

    def get_matches(self) -> np.ndarray:
        """
        Returns the current matching results.

        Returns
        -------
        np.ndarray
            An array of integer values representing the indices of the matched
            rows or columns. A value of `-1` indicates no match.
        """
        return self.__matches

    def rematch(self, i: int, items: np.ndarray):
        """
        Maintain unique matches by rematching 
        a duplicate match that does not 
        fall in favor as the best match for 
        the item.

        Parameters
        ----------
        i : int
            The current index of the row 
            and column to find the best match.
        items : np.ndarray
            The current row or column of 
            items to find the best match.
        """
        # The row/column index that best matches the column/row.
        max_index = np.argmax(items)
        if self.__limit and items[max_index] <= self.__min_value:
            return

        # Maintain unique matches.
        if max_index in self.__matches:
            # The row/column that is already matched.
            j = np.nonzero(self.__matches == max_index)[0]
            if (self.__matrix[(j, max_index) if self.__axis == 0
                              else (max_index, j)] <= items[max_index]):

                # Unmatch previous because current match is a better fit.
                self.__matches[j] = -1
                # Match the current column/row with the row/column.
                self.__matches[i] = max_index

                items = self.__matrix[(j, slice(None)) if self.__axis == 0
                                      else (slice(None), j)]
                items = np.squeeze(items)

                # Rematch previous match.
                i = j

            # Reassign the highest value to the minimum - 1 to take
            # the second highest value as the next potential match.
            items[max_index] = np.min(items) - 1
            # If i has not changed to j, rematch current match.
            self.rematch(i=i, items=items)

        else:
            self.__matches[i] = max_index  # Add a new match.

    def run(self):
        """
        Recursive matching algorithm which iterates
        over the rows or columns depending on the axis
        specified and finds the best match for each
        row or column. 

        The method iterates through the matrix, applying the `rematch` method
        on each row or column, depending on the axis specified.
        """
        for i in range(self.__matrix.shape[self.__axis]):
            self.rematch(
                i=i,
                items=self.__matrix[(i, slice(None)) if self.__axis == 0
                                    else (slice(None), i)]
            )
