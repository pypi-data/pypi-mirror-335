class Cache:
    def __init__(self, limit: int = 10000) -> None:
        self.limit: int = limit  # Maximum number of items the cache can store
        self.cache: dict[str, Node] = {}  # Hash map for O(1) access (key: str, value: Node)
        self.order: DoublyLinkedList = DoublyLinkedList()  # Doubly linked list to maintain order
        self.size: int = 0  # Current size of the cache
    
    def get(self, key: str) -> any:
        """Get the value from the cache if it exists."""
        if key in self.cache:
            # Move the accessed item to the most recent position
            self.order.move_to_end(self.cache[key])
            return self.cache[key].value
        return None
    
    def delete(self, key: str) -> None:
        """Remove a specific key from the cache if it exists."""
        if key in self.cache:
            node = self.cache[key]
            self.order.remove(node)  # Remove from the linked list
            del self.cache[key]  # Remove from the dictionary
            self.size -= 1
            
    def store(self, key: str, value: any) -> None:
        """Store a key-value pair in the cache."""
        if key in self.cache:
            # Update the value and move it to the most recent position
            node = self.cache[key]
            node.value = value
            self.order.move_to_end(node)
        else:
            # Add new key-value pair
            if self.size == self.limit:
                self.cleanup(0.1)  # Run cleanup if cache is full
            node = self.order.add(key, value)
            self.cache[key] = node
            self.size += 1
    
    def cleanup(self, percentage: float) -> None:
        """Remove the oldest items from the cache based on the given percentage."""
        num_to_remove: int = int(self.size * percentage)
        for _ in range(num_to_remove):
            # Remove the oldest items
            self.order.remove_oldest()
            self.size -= 1
            # Remove from the hash map as well
            del self.cache[self.order.head.key]


class Node:
    def __init__(self, key: str, value: int) -> None:
        self.key: str = key  # The key for this node
        self.value: int = value  # The value for this node
        self.prev: Node | None = None  # Pointer to the previous node in the list
        self.next: Node | None = None  # Pointer to the next node in the list


class DoublyLinkedList:
    def __init__(self) -> None:
        self.head: Node | None = None  # The head (oldest) node of the list
        self.tail: Node | None = None  # The tail (most recent) node of the list
    
    def add(self, key: str, value: int) -> Node:
        """Add a new node with the given key and value to the end of the list."""
        new_node: Node = Node(key, value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        return new_node
    
    def move_to_end(self, node: Node) -> None:
        """Move the given node to the end (most recent position) of the list."""
        if node == self.tail:
            return
        # Disconnect the node from the list
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if node == self.head:
            self.head = node.next
        
        # Move the node to the end
        self.tail.next = node
        node.prev = self.tail
        self.tail = node
        node.next = None
    
    def remove_oldest(self) -> Node | None:
        """Remove the oldest node (head of the list)."""
        if not self.head:
            return None
        oldest: Node = self.head
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        return oldest
    
    def remove(self, node: Node) -> None:
        """Remove a specific node from the list."""
        if not node:
            return
        
        # If the node is the head, move head forward
        if node == self.head:
            self.head = node.next
            if self.head:  # If there's a new head, update its prev reference
                self.head.prev = None
        # If the node is the tail, move tail backward
        if node == self.tail:
            self.tail = node.prev
            if self.tail:  # If there's a new tail, update its next reference
                self.tail.next = None
        # If it's in the middle, unlink it
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev