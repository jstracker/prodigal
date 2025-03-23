
    def generate_slots1(self):
        num_rows = int(self.num_slots / self.max_per_row) + (self.num_slots % self.max_per_row > 0)
        blanks = [
            (num_rows - 1, pos)
            for pos in range(self.max_per_row - (self.num_slots % self.max_per_row) - 1, self.max_per_row)
        ]
        #[any([pos < 0) for pos in (x, y)], ]
        #[x < 0, y < 0, (x, y) in blanks]
        #for position in range(self.num_slots)
        #        slot = {'up': position, 'down': (), 'left': (), 'right': (), 'item': None, 'image': None}
        """
        for row in range(num_rows)
            for x in range(self.max_per_row)
                if new_slots <= self.num_slots:
                    self.items.append
        """
        new_slots = 0
        self.slots = [
            [
                {
                    'up': (x, row - 1),
                    'down': (x, row + 1),
                    'left': (x - 1, row),
                    'right': (x + 1, row),
                    'item': None,
                    'image': None
                }
                for x in range(self.max_per_row)
                if (new_slots := new_slots + 1) <= self.num_slots
            ]
            for row in range(num_rows)
        ]


