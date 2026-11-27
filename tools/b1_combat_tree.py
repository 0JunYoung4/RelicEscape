"""Priority behavior tree for B1's opening and repeating attacks."""

from enum import Enum, auto


class Status(Enum):
    FAILURE = auto()
    RUNNING = auto()
    SUCCESS = auto()


class Attack(Enum):
    CLAW = auto()
    JUMP = auto()


OPENING = (Attack.CLAW, Attack.JUMP)


def _selector(*children):
    def tick(stage, dt):
        for child in children:
            result = child(stage, dt)
            if result is not Status.FAILURE:
                return result
        return Status.FAILURE
    return tick


def _guard(condition, action):
    def tick(stage, dt):
        return action(stage, dt) if condition(stage) else Status.FAILURE
    return tick


class B1CombatTree:
    def __init__(self):
        self.root = _selector(
            _guard(lambda stage: stage.health.current == 0, self._defeat),
            _guard(lambda stage: self.attack is not None, self._continue_attack),
            _selector(
                _guard(lambda stage: self.completed < len(OPENING), self._opening_attack),
                _guard(lambda stage: self.streak >= 2, self._switch_attack),
                _guard(lambda stage: stage.player_in_claw_range, self._start_claw),
                self._start_jump,
            ),
        )
        self.reset()

    def reset(self):
        self.attack = self.last_attack = None
        self.completed = self.streak = 0

    def tick(self, stage, dt):
        return self.root(stage, dt)

    def _defeat(self, stage, dt):
        self.attack = None
        stage.end_combat()
        return Status.RUNNING

    def _continue_attack(self, stage, dt):
        result = stage.advance_attack(dt)
        if result is Status.SUCCESS:
            self.completed += 1
            self.streak = self.streak + 1 if self.last_attack is self.attack else 1
            self.last_attack, self.attack = self.attack, None
        return result

    def _opening_attack(self, stage, dt):
        return self._start(stage, OPENING[self.completed])

    def _switch_attack(self, stage, dt):
        return self._start(stage, Attack.JUMP if self.last_attack is Attack.CLAW else Attack.CLAW)

    def _start_claw(self, stage, dt):
        return self._start(stage, Attack.CLAW)

    def _start_jump(self, stage, dt):
        return self._start(stage, Attack.JUMP)

    def _start(self, stage, attack):
        self.attack = attack
        stage.start_attack(attack)
        return Status.RUNNING
