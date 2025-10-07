from datetime import datetime


class StateBuffer:

    def __init__(self, size_sec: int):
        self.changes = list()
        self.size_sec = size_sec
        self.update(True)

    def update(self, new_state:bool):
        self.changes.append((datetime.now(), new_state))
        self.__compact()

    def __current_state(self) -> bool:
        return  self.changes[0][1]

    def __compact(self):
        new_changes = []
        if len(self.changes) > 1:
            for i in range(0, len(self.changes)-1):
                age = (datetime.now() - self.changes[i][0]).total_seconds()
                if age < self.size_sec:
                    new_changes.append(self.changes[i])
            new_changes.append(self.changes[-1])
            self.changes = new_changes

    def average_value(self) -> bool:
        if len(self.changes) == 1:
            return self.__current_state()
        else:
            on_sec = 0
            off_sec = 0
            for i in reversed(range(0, len(self.changes))):
                if i > 0:
                    elapsed = (self.changes[i][0] - self.changes[i-1][0]).total_seconds()
                    previous_state = self.changes[i-1][1]
                    if previous_state:
                        on_sec += elapsed
                    else:
                        off_sec += elapsed
            return True if on_sec > off_sec else False
