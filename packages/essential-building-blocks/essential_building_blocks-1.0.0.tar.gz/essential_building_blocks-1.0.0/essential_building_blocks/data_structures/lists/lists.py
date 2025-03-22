from essential_building_blocks.data_structures.common import (
    SingleLinkNode,
    DoubleLinkNode,
)
from typing import Any


class SingleLinkList:
    """
    A single linked list.
    """

    def __init__(self) -> None:
        self.head: SingleLinkNode | None = None
        self.tail: SingleLinkNode | None = None
        self.length: int = 0

    def is_empty(self) -> bool:
        """
        Checks if the list is empty.

        Returns:
            bool: True if the list is empty, False otherwise.
        """
        return self.length == 0

    def size(self) -> int:
        """
        Returns the size of the list.

        Returns:
            int: The size of the list.
        """
        return self.length

    def append_at_head(self, value: Any) -> None:
        """
        Adds a new node to the head of the list.

        Args:
            value (Any): The value of the new node.
        """
        new_node = SingleLinkNode(value)

        if self.is_empty() or self.head is None:
            self.__create_first_node(new_node)
        else:
            new_node.next = self.head
            self.head = new_node

        self.length += 1

    def append_at_tail(self, value: Any) -> None:
        """
        Adds a new node to the tail of the list.

        Args:
            value (Any): The value of the new node.
        """
        new_node = SingleLinkNode(value)

        if self.is_empty() or self.tail is None:
            self.__create_first_node(new_node)
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1

    def delete_at_head(self) -> None:
        """
        Deletes the node at the head of the list.

        Raises:
            IndexError: If the list is empty.
        """
        if self.is_empty() or self.head is None:
            raise IndexError("List is empty")

        prev_head = self.head
        self.head = self.head.next
        self.length -= 1

        # free memory
        del prev_head

    def delete_at_tail(self) -> None:
        """
        Deletes the node at the tail of the list.

        Raises:
            IndexError: If the list is empty.
        """

        if self.is_empty() or self.head is None:
            raise IndexError("List is empty")

        else:
            prev_tail = self.tail
            current_node = self.head

            # iterate to the second last node
            while current_node.next is not None:
                current_node = current_node.next

            self.tail = current_node
            self.tail.next = None

        self.length -= 1

        # free memory
        del prev_tail

    def __create_first_node(self, node: SingleLinkNode) -> None:
        """
        Helper method to create the first node in the list.

        Args:
            node (SingleLinkNode): The node to create.
        """
        self.head = node
        self.tail = node

    def __len__(self):
        return self.length

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __str__(self):
        return str([str(x) for x in self])

    def __repr__(self):
        return str(self)


class DoubleLinkList:
    """
    A double linked list.
    """

    def __init__(self) -> None:
        self.head: DoubleLinkNode | None = None
        self.tail: DoubleLinkNode | None = None
        self.length: int = 0

    def is_empty(self) -> bool:
        """
        Checks if the list is empty.

        Returns:
            bool: True if the list is empty, False otherwise.
        """
        return self.length == 0

    def size(self) -> int:
        """
        Returns the size of the list.

        Returns:
            int: The size of the list.
        """
        return self.length

    def append_at_head(self, value: Any) -> None:
        """
        Adds a new node to the head of the list.

        Args:
            value (Any): The value of the new node.
        """
        new_node = DoubleLinkNode(value)

        if self.is_empty() or self.head is None:
            self.__create_first_node(new_node)
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self.length += 1

    def append_at_tail(self, value: Any) -> None:
        """
        Adds a new node to the tail of the list.

        Args:
            value (Any): The value of the new node.
        """
        new_node = DoubleLinkNode(value)

        if self.is_empty() or self.tail is None:
            self.__create_first_node(new_node)
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

        self.length += 1

    def delete_at_head(self) -> None:
        """
        Deletes the node at the head of the list.

        Raises:
            IndexError: If the list is empty.
        """
        if self.is_empty() or self.head is None:
            raise IndexError("List is empty")

        # update next pointer
        prev_head = self.head
        self.head = self.head.next

        # update prev pointer
        if self.head is not None:
            self.head.prev = None

        self.length -= 1

        # free memory
        del prev_head

    def delete_at_tail(self) -> None:
        """
        Deletes the node at the tail of the list.

        Raises:
            IndexError: If the list is empty.
        """
        if self.is_empty() or self.tail is None:
            raise IndexError("List is empty")

        # update prev pointer
        prev_tail = self.tail
        self.tail = self.tail.prev

        # update next pointer
        if self.tail is not None:
            self.tail.next = None

        self.length -= 1

        # free memory
        del prev_tail

    def __create_first_node(self, node: DoubleLinkNode) -> None:
        """
        Helper method to create the first node in the list.

        Args:
            node (DoubleLinkNode): The node to create.
        """
        self.head = node
        self.tail = node

        node.next = None
        node.prev = None

    def __len__(self):
        return self.length

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __str__(self):
        return str([str(x) for x in self])

    def __repr__(self):
        return str(self)


class Stack(DoubleLinkList):
    """
    A stack implemented using a double linked list.
    """

    def push(self, value: Any) -> None:
        """
        Pushes a new value onto the stack.

        Args:
            value (Any): The value to push.
        """
        self.append_at_head(value)

    def pop(self) -> Any:
        """
        Removes and returns the value at the top of the stack.

        Raises:
            IndexError: If the stack is empty.

        Returns:
            Any: The value at the top of the stack.
        """

        if self.is_empty() or self.head is None:
            raise IndexError("Stack is empty")

        data: Any = self.head.value
        self.delete_at_head()
        return data

    def peek(self) -> Any:
        """
        Returns the value at the top of the stack without removing it.

        Raises:
            IndexError: If the stack is empty.

        Returns:
            Any: The value at the top of the stack.
        """
        if self.is_empty() or self.head is None:
            raise IndexError("Stack is empty")

        return self.head.value


class Queue(DoubleLinkList):
    """
    A queue implemented using a double linked list.
    """

    def enqueue(self, value: Any) -> None:
        """
        Adds a new element to the end of the queue.

        Args:
            value (Any): The value to be added to the queue.
        """

        self.append_at_tail(value)

    def dequeue(self) -> Any:
        """
        Removes and returns the value at the front of the queue.

        Raises:
            IndexError: If the queue is empty.

        Returns:
            Any: The value at the front of the queue.
        """
        if self.is_empty() or self.head is None:
            raise IndexError("Queue is empty")

        data: Any = self.head.value
        self.delete_at_head()
        return data

    def peek(self) -> Any:
        """
        Returns the value at the front of the queue without removing it.

        Raises:
            IndexError: If the queue is empty.

        Returns:
            Any: The value at the front of the queue.
        """

        if self.is_empty() or self.head is None:
            raise IndexError("Queue is empty")

        return self.head.value


class FixedSizeArray:
    """
    A fixed-size array implemented using the built-in list data type.
    """

    def __init__(self, size: int, data_type: type | None = None):
        # Validate size
        if not isinstance(size, int):
            raise TypeError("Size must be an integer")
        if size < 0:
            raise ValueError("Size must be non-negative")

        self.size: int = size
        self.__type = data_type
        self.__array: list = [None] * size

    def __iter__(self):
        return iter(self.__array)

    def __len__(self):
        return self.size

    def __getitem__(self, index: int) -> Any:
        return self.__array[index]

    def __setitem__(self, index: int, value: Any) -> None:
        # check type
        if self.__type is not None and not isinstance(value, self.__type):
            raise TypeError(
                f"Expected {self.__type.__name__}, got {type(value).__name__}"
            )

        self.__array[index] = value

    def __str__(self):
        return str(self.__array)

    def __repr__(self):
        return str(self)
