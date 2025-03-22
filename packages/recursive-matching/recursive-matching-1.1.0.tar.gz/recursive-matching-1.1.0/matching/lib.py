"""Module for the placeholder of the recursive_match function."""

import numpy as np

from .recursive_match import Matcher


def recursive_match(
    matrix: np.ndarray,
    axis: int = 1,
    limit: bool = True,
    minimum: bool = False
) -> np.ndarray:
    """
    Runs the recursive algorithm to generate the assignments.

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
    minimum : bool
        Match based on the smaller value in the matrix. By default,
        the matches are based on the highest value.

    Returns
    -------
    np.ndarray
        This is a one-dimensional array. If axis is specified to 0,
        this array will have the same length as the rows. If axis is
        specified to 1, this array will have the same length as the
        columns. The values are the indices of rows (axis=1) or columns
        (axis=0) that are the best match. If the value is -1, this
        means there is no match for this particular row/column.
    """
    if axis not in [0, 1]:
        print(f"\t - [ERROR] Axis can only be 0 or 1. Got {axis}")
        return

    if minimum:
        # The smallest values becomes the largest values.
        matrix = -1 * (matrix - np.max(matrix))

    matcher = Matcher(matrix=matrix, axis=axis, limit=limit)
    matcher.run()

    return matcher.get_matches()


if __name__ == '__main__':
    mat = np.array([
        [0.,         0.,         0.,         0.,         0.],
        [0.20689655, 0.07407407, 0.04761905, 0.,         0.23076923],
        [0.,         0.,         0.38461538, 0.,         0.,],
        [0.,         0.,         0.04347826, 0.5,        0.,],
        [0.5,        0.,         0.,         0.,         1.,]
    ], dtype=np.float32)

    matches = recursive_match(matrix=mat)
    print(f"Matches: {matches}")
