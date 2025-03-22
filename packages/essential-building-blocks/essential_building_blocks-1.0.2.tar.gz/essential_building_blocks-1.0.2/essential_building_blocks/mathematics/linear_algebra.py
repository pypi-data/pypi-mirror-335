from essential_building_blocks.data_structures.lists import FixedSizeArray


class Vector(FixedSizeArray):
    """
    A vector in n-dimensional space.
    """

    def __init__(self, dimensions: int):
        """
        A vector in n-dimensional space.

        Args:
            dimensions (int): The dimensionality of the vector.
        """
        super().__init__(size=dimensions, data_type=float)

        self.dimensions: int = dimensions

    def normalized(self) -> "Vector":
        """
        Normalize the vector.

        Returns:
            Vector: A new vector instance representing the normalized vector.
        """

        temp: Vector = Vector(dimensions=self.dimensions)

        for index, scalar in enumerate(self):
            temp[index] = scalar / self.magnitude()

        return temp

    def magnitude(self) -> float:
        """
        Calculate the magnitude of the vector.

        Returns:
            float: The magnitude of the vector.
        """
        sum_of_squares: float = 0

        for scalar in self:
            sum_of_squares += scalar**2

        return sum_of_squares**0.5
