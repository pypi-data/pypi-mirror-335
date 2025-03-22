"""
The goal is
1. The logic of the evaluation will be in a class specific to this evaluation
scheme.
2. New evaluation scheme can be added anytime.
3. Airflow jobs run every night to analyse all the interactions of the day for
scenes associated with a scene template which has an evaluation scheme
attached to it. based on the evaluation scheme the interactions will be
evaluated and grades is created and stored for the student.
"""


class BaseEvaluationScheme:
    name = "base_scheme"

    def __init__(self):
        ...

    def analyze(self):
        ...
