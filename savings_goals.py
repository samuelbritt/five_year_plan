from operator import itemgetter, attrgetter

import month

class SavingsGoal(object):
    def __init__(self, name, target_amount, target_month):
        super().__init__()
        self.name = name
        self.target_amount = target_amount
        self.target_month = target_month

        self.amount_saved = 0

    def __repr__(self):
        return "{cls}({name}, {amt:.2f}, {tgt_month})".format(cls=self.__class__.__name__,
                                                          name=repr(self.name),
                                                          amt=self.target_amount,
                                                          tgt_month=repr(self.target_month))

    def __str__(self):
        return "{cls}({name}, {amt:.2f}, {tgt_month})".format(cls=self.__class__.__name__,
                                                          name=repr(self.name),
                                                          amt=self.target_amount,
                                                          tgt_month=str(self.target_month))
    def save(self, amount):
        self.amount_saved += amount

    @property
    def amount_left(self):
        return self.target_amount - self.amount_saved

class SavingsGoals(object):
    def __init__(self, savings_goals=[]):
        super().__init__()
        self.savings_goals = savings_goals

    def add_goal(self, goal):
        self.savings_goals.append(goal)
    
    def calculate_savings_plan(self, amount_available):
        """ `amount_available` is a dictionary of {target_month: amount_available} KV pairs """

        # Work backwards from the goal furthest in the future
        max_target_month = max(self.savings_goals, key=attrgetter('target_month')).target_month

        # sanity check on input
        max_month_available = max(amount_available)
        if max_target_month > max_month_available:
            raise("Target goals outside of specified income")

        # Iterate, starting at max
        this_month = max_target_month
        savings_plan = {}
        while self.have_goals():
            amount_for_month = amount_available[this_month]
            savings_plan[this_month] = {}
            savings_plan[this_month]['amount_available'] = amount_for_month
            
            goals_for_month = sorted(self.goals_for_month(this_month), key=attrgetter('amount_left'))
            goal_count = len(goals_for_month)
            amount_for_each_goal = float(amount_for_month) / max(goal_count, 1)
            for g in goals_for_month:
                amount_for_this_goal = min(amount_for_each_goal, g.amount_left)
                g.save(amount_for_this_goal)
                savings_plan[this_month][g]=amount_for_this_goal

                amount_for_month -= amount_for_this_goal
                print(g.amount_left, goal_count)
                if g.amount_left == 0.00:
                    goal_count -= 1
                    amount_for_each_goal = float(amount_for_month) / max(goal_count, 1)

    
            this_month = this_month.monthadd(-1)
        return savings_plan

    def goals_for_month(self, this_month):
        goals = []
        for g in self.savings_goals:
            if g.target_month > this_month and g.amount_left > 0:
                goals.append(g)
        return goals

    def have_goals(self):
        for g in self.savings_goals:
            if g.amount_left > 0:
                return True
        return False
