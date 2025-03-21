import numpy as np


def hungarian_match(matrix: np.ndarray, axis: int=1, minimum: bool=True) -> np.ndarray: # NOSONAR
    """
    Hungarian algorithm implementation for optimal assignments.

    Parameters
    ----------
    matrix : np.ndarray
        The input matrix as a 2D array. Each row 
        can only be matched to one item in the
        column or vice versa.
    axis : int
       The array returned is a 1D matrix with the length
       based on the matrix axis length. If axis is specified to 0,
       the length of the matches is the length of the rows and the
       values are the index of the columns it is matched. If axis
       is specified to 1, the length of the matches is the length of
       the columns and the values are the index of the rows it is matched.
    minimum : bool
        Match based to yeild the smallest sum (default). If set to False,
        match based on the highest sum.
    
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
        print(f"\t - [WARNING]: Axis can only between 0 or 1. Got {axis}")
        return
    
    def pad_matrix(matrix: np.ndarray) -> np.ndarray:
        """
        Pad a matrix with zeros to ensure a square matrix.

        Parameters
        ----------
        matrix : np.ndarray
            The 2D input matrix.

        Returns
        -------
        np.ndarray 
            The padded 2D square matrix 
            where the number of rows equals columns.
        """
        rows, cols = matrix.shape
        if rows == cols:
            return matrix
        
        size = max(rows, cols)
        padded_matrix = np.zeros((size, size), dtype=np.float32)
        padded_matrix[:rows, :cols] = matrix
        return padded_matrix

    def lines(indices: np.ndarray) -> list:
        """
        Form a line from a set of indices.
        Items in the indices that are duplicated
        are considered to form one line in the matrix 
        covering the zeros.

        Parameters
        ----------
        indices : np.ndarray
            These are the indices of the zero either
            the row indices or the column indices. 
            Zeros in the same row or column forms an
            optimal line.

        Returns
        -------
        list
            Since duplicated index locations of zeros are one line. For
            each duplicated value represents one line. This list will
            contain a list for every line. Each list contains
            the index of the zeros that belongs to that line.
        """
        # Find where index of zeros contains common/duplicated values.
        unique, counts = np.unique(indices, return_counts=True)
        common = unique[counts > 1]
        # The index of the zeros forming a line.
        # Group the indices into separate lists for each duplicated value
        return [np.nonzero(indices == val)[0].tolist() for val in common if val >= 0]
    
    def all_lines(zeros: np.ndarray) -> list:
        """
        Collect all the lines in the current matrix state.

        Parameters
        ----------
        zeros : np.ndarray
            The (row index, column index) locations
            of the zeros in the matrix. This has shape
            (n, 2).

        Returns
        -------
        list
            A list of list where each list
            contains the zero positions that belong to the line.
            Each list represents a line. There are cases where
            one list will only contain one zero.
        """
        total_lines = []
    
        # Find the index in the zeros forming a row line.
        row_lines = lines(indices=zeros[:, 0])

        # Add each row line to the total lines.
        for line in row_lines:
            total_lines.append(zeros[line])

        column_zeros = zeros.copy()
        
        # These indices already formed a line.
        if len(row_lines):
            discard_indices = np.concatenate(row_lines).tolist()
            column_zeros[discard_indices] = -1

        # Find the index in the zeros forming a column line.
        column_lines = lines(indices=column_zeros[:, 1])

        # Add each column line to the total lines.
        for line in column_lines:
            total_lines.append(zeros[line])

        # A separate line is attributed to the rest of the zeros.
        if len(column_lines):
            discard_indices = np.concatenate(column_lines).tolist()
            column_zeros[discard_indices] = -1

        # Each element is the index of one zero forming one line.
        remaining_lines = np.nonzero(column_zeros[:, 0] >= 0)[0]
        
        # Add a line for each remaining zero.
        for line in remaining_lines:
            total_lines.append(zeros[line])

        return total_lines
    
    def add_lines(total_lines: list, matrix: np.ndarray) -> np.ndarray:
        """
        Implementation of step 5 in the process which seeks to identify 
        smallest uncovered value. Add this value to the values covered by 
        two lines. Subtract this value from the values that are not 
        covered by any line.

        Parameters
        ----------
        total_lines : list
            A list of list where each list
            contains the zero positions that belong to the line.
            Each list represents a line. There are cases where
            one list will only contain one zero.
        matrix : np.ndarray
            2D input matrix with zeros after previous
            steps in the process.

        Returns
        -------
        np.ndarray
            The modified input matrix after the logic
            defined in this method. 
        """
        # A list of all possible positions in the matrix.
        indices = list(np.ndindex(matrix.shape))
        # Counts of the occurences of the positions being covered by lines.
        covered_counts = np.zeros(len(indices), dtype=np.int32)

        # Positions in the matrix uncovered by the lines.
        uncovered_positions = list(np.ndindex(matrix.shape))

        # Finding positions in the matrix uncovered by the lines.
        for line in total_lines:
            # Indicate multiple zeros are covered.
            if len(line.shape) > 1:
                # The line covers a row.
                if len(np.unique(line[:, 0])) == 1:
                    row_index = np.unique(line[:, 0])[0]
                    for col in range(matrix.shape[1]):
                        position = (row_index, col)
                        covered_counts[indices.index(position)] += 1
                        if position in uncovered_positions:
                            uncovered_positions.remove((row_index, col))
                # The line covers a column.
                elif len(np.unique(line[:, 1])) == 1:
                    column_index = np.unique(line[:, 1])[0]
                    for row in range(matrix.shape[0]):
                        position = (row, column_index)
                        covered_counts[indices.index(position)] += 1
                        if position in uncovered_positions:
                            uncovered_positions.remove((row, column_index))
            # Indicate a single zero is covered.
            else:
                row_index = line[0]
                for col in range(matrix.shape[1]):
                    position = (row_index, col)
                    covered_counts[indices.index(position)] += 1
                    if position in uncovered_positions:
                        uncovered_positions.remove((row_index, col))

        # Identify smallest uncovered value.
        uncovered_positions = np.reshape(uncovered_positions, (-1, 2))
        uncovered_values = matrix[uncovered_positions[:, 0], uncovered_positions[:, 1]]
        uncovered_minimum = np.min(uncovered_values)

        # Subtract uncovered values by the smallest uncovered value.
        matrix[uncovered_positions[:, 0], uncovered_positions[:, 1]] -= uncovered_minimum

        # Add values covered twice with the smallest uncovered value.
        indices = np.reshape(indices, (-1, 2))
        covered_positions = indices[covered_counts > 1]
        matrix[covered_positions[:, 0], covered_positions[:, 1]] += uncovered_minimum
        
        return matrix
    
    def zero(matrix: np.ndarray) -> np.ndarray:
        """
        Find the positions of the zeros in the matrix.

        Parameters
        ----------
        matrix : np.ndarray
            The 2D matrix containing zeros.

        Returns
        -------
        np.ndarray
            An array of shape (n, 2) which marks
            the locations (row index, column index) of 
            the zeros in the matrix.
        """
        zeros = np.nonzero(matrix == 0)
        zeros = np.hstack((zeros[0][:, np.newaxis], zeros[1][:, np.newaxis]), 
                          dtype=np.int32)
        return zeros

    def process(matrix: np.ndarray):
        """
        Running the 6-step process of the hungarian
        algorithm. The following steps are outlined.

        1) Subtract row minima.
        2) Subtract column minima.
        3) Cover zeros with lines.
        4) Check for optimal solution. Proceed to step 5 if not.
        5) Create additional lines. Identify smallest uncovered value.
           Add this value to the values covered by two lines. 
           Subtract this value from the values that are not covered by any line.
        6) Check for optimal solution. Repeat steps 1-5 if not.

        Parameters
        ----------
        matrix : np.ndarray
            The 2D matrix input array for finding
            the optimized assignments.

        Returns
        -------
        list 
            A list of list where each list
            contains the zero positions that belong to the line.
            Each list represents a line. There are cases where
            one list will only contain one zero. The number of lines
            will equal the size of the matrix.
        """
        # Step 1: Subtract row minima.
        row_minimums = np.min(matrix, axis=1)
        matrix_minus_row = matrix - row_minimums[:, np.newaxis]

        # Step 2: Subtract column minima.
        column_minimums = np.min(matrix_minus_row, axis=0)
        matrix_minus_column = matrix_minus_row - column_minimums[np.newaxis, :]
        
        # Step 3. Cover zeros with lines.
        zeros = zero(matrix=matrix_minus_column)
        total_lines = all_lines(zeros)    

        # Step 4. Check for optimal solution. Proceed to step 5 if not.
        if len(total_lines) < matrix.shape[0]:

            # Step 5. Create additional lines. Identify smallest uncovered value.
            # Add this value to the values covered by two lines. Subtract this value
            # from the values that are not covered by any line.

            matrix_minus_column = add_lines(
                total_lines=total_lines, 
                matrix=matrix_minus_column
            )

            # Step 5.1. Check for optimal solution. Repeat steps 1-5 if not.
            zeros = zero(matrix=matrix_minus_column)
            total_lines = all_lines(zeros)
            if len(total_lines) < matrix.shape[0]:
                process(matrix=matrix_minus_column)

        return total_lines
    
    # The hungarian algorithm requires a square matrix. 
    matrix = pad_matrix(matrix=matrix)
    
    # Find the maximum assignments.
    if not minimum:
        # Convert to minimization by subtracting 
        # each element from the max in each row
        row_max = matrix.max(axis = 1).reshape(-1, 1) # Get row-wise max.
        matrix = row_max - matrix  # Convert to cost matrix for minimization.

    optimal_lines = process(matrix)

    # Step 6. Formulate matches depending on the axis provided.
    matches = np.ones(matrix.shape[axis], dtype=np.int32) * -1 
    
    #  A line with only one zero represents a mandatory assignment.
    single_zeros = [] # Lines formed by a single zero.
    multi_zeros = [] # Lines formed by multiple zeros.
    
    # This needs to be optimized: TODO.
    for line in optimal_lines:
        # Indicates multiple zeros are covered.
        if len(line.shape) > 1:
            multi_zeros.append(line)
        else:
            single_zeros.append(line)

    for z in single_zeros:
        match_index = z[axis]
        match_value = z[int(not axis)]

        if match_value in matches:
                continue

        # Current position does not currently have a match.
        if matches[match_index] < 0:
            matches[match_index] = match_value

    for zeros in multi_zeros:
        for z in zeros:
            match_index = z[axis]
            match_value = z[int(not axis)]

            if match_value in matches:
                continue

            # Current position does not currently have a match.
            if matches[match_index] < 0:
                matches[match_index] = match_value

    return matches

if __name__ == '__main__':
    matrix = np.array([
        [30,40,50,60],
        [70,30,40,70],
        [60,50,60,30],
        [20,80,50,70]
    ], dtype=np.float32)
    matches = hungarian_match(matrix=matrix)
    print(f"{matches=}")


    # Compare the matches with the matrix from the recursive matching.
    matrix = np.array([
        [0.,         0.,         0.,         0.,         0.        ],
        [0.20689655, 0.07407407, 0.04761905, 0.,         0.23076923],
        [0.,         0.,         0.38461538, 0.,         0.,        ],
        [0.,         0.,         0.04347826, 0.5,        0.,        ],
        [0.5,        0.,         0.,         0.,         1.,        ]
    ], dtype=np.float32)

    matches = hungarian_match(matrix=matrix, minimum=False)
    print(f"{matches=}")