from control.acciones import NADA
import config.settings as settings


class Rule:

    def __init__(self, name, condition, action, priority):
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority

    def check(self, state):
        return self.condition(state)


class RuleEngine:

    def __init__(self, rules):

        # menor número = mayor prioridad
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.debug_reglas = bool(getattr(settings, "DEBUG_REGLAS", False))

    def decide(self, state):

        for rule in self.rules:

            if rule.check(state):
                if self.debug_reglas:
                    print(f"[REGLA] {rule.name} se activó.")
                return rule.action

        return NADA
