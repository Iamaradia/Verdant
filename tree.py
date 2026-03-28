import pygame
import json

class Tree:
    def __init__(self, duration):
        self.elapsed = 0
        self.duration = duration

        self.upvotes = 0
        self.downvotes = 0
        self.start_note = ""
        self.end_note = ""

    def update(self, dt):
        self.elapsed = min(self.duration, self.elapsed + dt)

    def is_finished(self):
        return self.elapsed >= self.duration

    def to_json(self):
        return json.dumps({
            "elapsed": self.elapsed,
            "duration": self.duration,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "start_note": self.start_note,
            "end_note": self.end_note
        })