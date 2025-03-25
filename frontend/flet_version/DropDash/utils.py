from collections import OrderedDict

class LimitedCache(OrderedDict):
            def __init__(self, max_size=10):
                self.max_size = max_size
                super().__init__()

            def __setitem__(self, key, value):
                if len(self) >= self.max_size:
                    self.popitem(last=False)  # remove the oldest item
                super().__setitem__(key, value)