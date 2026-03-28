from timer import Timer
from tree import Tree

class Session:
    def __init__(self, duration):
        self.tree = Tree(duration)

    def update(self, dt):
        self.tree.update(dt)

    def is_finished(self):
        return self.tree.is_finished()