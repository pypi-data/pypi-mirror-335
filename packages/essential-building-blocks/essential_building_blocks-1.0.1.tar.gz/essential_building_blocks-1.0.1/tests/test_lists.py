from pytest import raises
from essential_building_blocks.data_structures.lists import (
    SingleLinkList,
    DoubleLinkList,
    Stack,
    Queue,
    FixedSizeArray,
)
from essential_building_blocks.data_structures.common import (
    SingleLinkNode,
    DoubleLinkNode,
)


class TestSingleLinkNode:
    def test_init(self):
        node = SingleLinkNode(1)
        assert node.value == 1
        assert node.next is None

    def test_init_with_next(self):
        node = SingleLinkNode(1, SingleLinkNode(2))
        assert node.value == 1
        assert node.next.value == 2

    def test_str(self):
        node = SingleLinkNode(1)
        assert node.__str__() == "1"

    def test_repr(self):
        node = SingleLinkNode(1)
        assert node.__repr__() == "1"


class TestSingleLinkList:
    def test_init(self):
        sll = SingleLinkList()
        assert sll.head is None
        assert sll.tail is None
        assert sll.length == 0

    def test_is_empty(self):
        sll = SingleLinkList()
        assert sll.is_empty() is True

    def test_size(self):
        sll = SingleLinkList()
        assert sll.size() == 0

        sll.append_at_head(1)
        sll.append_at_head(2)
        assert sll.size() == 2

    def test_append_at_head(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        assert sll.head.value == 2
        assert sll.head.next.value == 1

    def test_append_at_tail(self):
        sll = SingleLinkList()
        sll.append_at_tail(1)
        sll.append_at_tail(2)
        assert sll.tail.value == 2
        assert sll.tail.next is None

    def test_delete_at_head(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        sll.delete_at_head()
        assert sll.head.value == 1

    def test_delete_at_head_empty(self):
        sll = SingleLinkList()
        with raises(IndexError):
            sll.delete_at_head()

    def test_delete_at_tail(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        sll.delete_at_tail()
        assert sll.tail.value == 1

    def test_delete_at_tail_empty(self):
        sll = SingleLinkList()
        with raises(IndexError):
            sll.delete_at_tail()

    def test_str(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        assert sll.__str__() == str([str(2), str(1)])

        sll = SingleLinkList()
        sll.append_at_tail(1)
        sll.append_at_tail(2)
        assert sll.__str__() == str([str(1), str(2)])

        sll = SingleLinkList()
        assert sll.__str__() == str([])

    def test_repr(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        assert sll.__repr__() == str([str(2), str(1)])

        sll = SingleLinkList()
        sll.append_at_tail(1)
        sll.append_at_tail(2)
        assert sll.__repr__() == str([str(1), str(2)])

        sll = SingleLinkList()
        assert sll.__repr__() == str([])

    def test_len(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        assert sll.__len__() == 2

    def test_iter(self):
        sll = SingleLinkList()
        sll.append_at_head(1)
        sll.append_at_head(2)
        assert list(sll) == [2, 1]


class TestDoubleLinkNode:
    def test_init(self):
        node = DoubleLinkNode(1)
        assert node.value == 1
        assert node.next is None
        assert node.prev is None

    def test_init_with_next(self):
        node = DoubleLinkNode(1, DoubleLinkNode(2))
        assert node.value == 1
        assert node.next.value == 2
        assert node.prev is None

    def test_init_with_prev(self):
        node = DoubleLinkNode(1, None, DoubleLinkNode(2))
        assert node.value == 1
        assert node.next is None
        assert node.prev.value == 2

    def test_init_with_next_and_prev(self):
        node = DoubleLinkNode(1, DoubleLinkNode(2), DoubleLinkNode(3))
        assert node.value == 1
        assert node.next.value == 2
        assert node.prev.value == 3

    def test_str(self):
        node = DoubleLinkNode(1)
        assert node.__str__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2))
        assert node.__str__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2), DoubleLinkNode(3))
        assert node.__str__() == str(1)

        node = DoubleLinkNode(1, None, DoubleLinkNode(2))
        assert node.__str__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2), None)
        assert node.__str__() == str(1)

        node = DoubleLinkNode(1, None, None)
        assert node.__str__() == str(1)

    def test_repr(self):
        node = DoubleLinkNode(1)
        assert node.__repr__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2))
        assert node.__repr__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2), DoubleLinkNode(3))
        assert node.__repr__() == str(1)

        node = DoubleLinkNode(1, None, DoubleLinkNode(2))
        assert node.__repr__() == str(1)

        node = DoubleLinkNode(1, DoubleLinkNode(2), None)
        assert node.__repr__() == str(1)

        node = DoubleLinkNode(1, None, None)
        assert node.__repr__() == str(1)


class TestDoubleLinkList:
    def test_init(self):
        dll = DoubleLinkList()
        assert dll.head is None
        assert dll.tail is None
        assert dll.length == 0

    def test_is_empty(self):
        dll = DoubleLinkList()
        assert dll.is_empty()

        dll.append_at_head(1)
        assert not dll.is_empty()

        dll.delete_at_head()
        assert dll.is_empty()

        dll.append_at_head(1)
        dll.append_at_head(2)
        assert not dll.is_empty()

        dll.delete_at_head()
        dll.delete_at_head()
        assert dll.is_empty()

    def test_size(self):
        dll = DoubleLinkList()
        assert dll.size() == 0

        dll.append_at_head(1)
        assert dll.size() == 1

        dll.append_at_head(2)
        assert dll.size() == 2

        dll.delete_at_head()
        assert dll.size() == 1

        dll.delete_at_head()
        assert dll.size() == 0

    def test_append_at_head(self):
        dll = DoubleLinkList()
        dll.append_at_head(1)
        dll.append_at_head(2)
        assert dll.size() == 2

    def test_append_at_tail(self):
        dll = DoubleLinkList()
        dll.append_at_tail(1)
        dll.append_at_tail(2)
        assert dll.size() == 2

    def test_delete_at_head(self):
        dll = DoubleLinkList()
        dll.append_at_head(1)
        dll.append_at_head(2)
        dll.delete_at_head()
        assert dll.size() == 1

        dll.delete_at_head()
        assert dll.size() == 0

        with raises(IndexError):
            dll.delete_at_head()

    def test_delete_at_tail(self):
        dll = DoubleLinkList()
        dll.append_at_head(1)
        dll.append_at_head(2)
        dll.delete_at_tail()
        assert dll.size() == 1

        dll.delete_at_tail()
        assert dll.size() == 0

        with raises(IndexError):
            dll.delete_at_tail()

    def test_str(self):
        dll = DoubleLinkList()
        assert dll.__str__() == "[]"

        dll.append_at_head(1)
        assert dll.__str__() == "['1']"

        dll.append_at_head(2)
        assert dll.__str__() == "['2', '1']"

        dll.delete_at_head()
        assert dll.__str__() == "['1']"

        dll.delete_at_head()
        assert dll.__str__() == "[]"

    def test_repr(self):
        dll = DoubleLinkList()
        assert dll.__repr__() == "[]"

        dll.append_at_head(1)
        assert dll.__repr__() == "['1']"

        dll.append_at_head(2)
        assert dll.__repr__() == "['2', '1']"

        dll.delete_at_head()
        assert dll.__repr__() == "['1']"

        dll.delete_at_head()
        assert dll.__repr__() == "[]"

    def test_iter(self):
        dll = DoubleLinkList()
        dll.append_at_head(1)
        dll.append_at_head(2)
        assert list(dll) == [2, 1]

    def test_len(self):
        dll = DoubleLinkList()
        dll.append_at_head(1)
        dll.append_at_head(2)
        assert len(dll) == 2


class TestStack:
    def test_init(self):
        stack = Stack()
        assert stack.size() == 0

    def test_is_empty(self):
        stack = Stack()
        assert stack.is_empty()

        stack.push(1)
        assert not stack.is_empty()

        stack.pop()
        assert stack.is_empty()

    def test_size(self):
        stack = Stack()
        assert stack.size() == 0

        stack.push(1)
        assert stack.size() == 1

        stack.push(2)
        assert stack.size() == 2

        stack.pop()
        assert stack.size() == 1

        stack.pop()
        assert stack.size() == 0

    def test_push(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        assert stack.size() == 2

    def test_pop(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        assert stack.pop() == 2
        assert stack.pop() == 1

        with raises(IndexError):
            stack.pop()

    def test_peek(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        assert stack.peek() == 2

        stack.pop()
        stack.pop()
        with raises(IndexError):
            stack.peek()


class TestQueue:
    def test_init(self):
        queue = Queue()
        assert queue.size() == 0

    def test_is_empty(self):
        queue = Queue()
        assert queue.is_empty()

        queue.enqueue(1)
        assert not queue.is_empty()

        queue.dequeue()
        assert queue.is_empty()

    def test_size(self):
        queue = Queue()
        assert queue.size() == 0

        queue.enqueue(1)
        assert queue.size() == 1

        queue.enqueue(2)
        assert queue.size() == 2

        queue.dequeue()
        assert queue.size() == 1

        queue.dequeue()
        assert queue.size() == 0

    def test_enqueue(self):
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        assert queue.size() == 2

    def test_dequeue(self):
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        assert queue.dequeue() == 1
        assert queue.dequeue() == 2

        with raises(IndexError):
            queue.dequeue()

    def test_peek(self):
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        assert queue.peek() == 1

        queue.dequeue()
        queue.dequeue()
        with raises(IndexError):
            queue.peek()


class TestFixedSizeArray:
    def test_init(self):
        array = FixedSizeArray(3)
        assert array.size == 3

    def test_invalid_size(self):
        with raises(ValueError):
            FixedSizeArray(-1)

        with raises(TypeError):
            FixedSizeArray("1")

    def test_getitem(self):
        array = FixedSizeArray(3)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        assert array[0] == 1
        assert array[1] == 2
        assert array[2] == 3

        with raises(IndexError):
            array[3]

    def test_setitem(self):
        array = FixedSizeArray(3)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        assert array[0] == 1
        assert array[1] == 2
        assert array[2] == 3

        with raises(IndexError):
            array[3] = 4

    def test_setitem_type(self):
        array = FixedSizeArray(3, int)
        with raises(TypeError):
            array[0] = "1"

        array = FixedSizeArray(3, str)
        with raises(TypeError):
            array[0] = 1

        array = FixedSizeArray(3, int)
        array[0] = 1

    def test_len(self):
        array = FixedSizeArray(3)
        assert len(array) == 3

    def test_iter(self):
        array = FixedSizeArray(3)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        assert list(array) == [1, 2, 3]

    def test_str(self):
        array = FixedSizeArray(3)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        assert str(array) == "[1, 2, 3]"

    def test_repr(self):
        array = FixedSizeArray(3)
        array[0] = 1
        array[1] = 2
        array[2] = 3
        assert repr(array) == "[1, 2, 3]"
