class Subject:
    def __init__(self, name, hours, credit, type_, lab_hours):
        self.name = name
        self.remaining = hours + credit
        self.type = type_
        self.lab_hours = lab_hours
        self.lab_assigned = False


class TimeTable:
    def __init__(self):
        self.table = [["" for _ in range(8)] for _ in range(5)]
        self.lab_day_used = [False]*5

    def allocate_lab(self, subjects):
        for s in subjects:
            if s.type in ["Lab","Integrated"] and not s.lab_assigned:
                req = s.lab_hours

                for i in range(5):
                    if self.lab_day_used[i]:
                        continue

                    for j in range(8-req+1):
                        if all(self.table[i][j+x]=="" for x in range(req)):
                            for x in range(req):
                                self.table[i][j+x] = s.name + " LAB"

                            self.lab_day_used[i] = True
                            s.lab_assigned = True
                            break
                    if s.lab_assigned:
                        break

    def allocate_theory(self, subjects):
        for i in range(5):
            for j in range(8):
                if self.table[i][j] == "":
                    max_sub = None

                    for s in subjects:
                        if s.type == "Theory" and (not max_sub or s.remaining > max_sub.remaining):
                            max_sub = s

                    if max_sub and max_sub.remaining > 0:
                        self.table[i][j] = max_sub.name
                        max_sub.remaining -= 1

    def fill_remaining(self, subjects):
        for i in range(5):
            for j in range(8):
                if self.table[i][j] == "":
                    for s in subjects:
                        if s.remaining > 0:
                            self.table[i][j] = s.name
                            s.remaining -= 1
                            break