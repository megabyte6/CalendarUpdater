import datetime
from enum import Enum


class Curriculum(Enum):
    CREATE = "CREATE"
    JR = "JR"


class Ninja:
    def __init__(self, name: str, curriculum: Curriculum):
        """
        Initializes a Code Ninjas student.

        Args:
            name: The name of the student.
            curriculum: The curriculum the student is in.
        """

        self.name = name
        self.curriculum = curriculum

    def __repr__(self) -> str:
        return f"Ninja(name={self.name}, curriculum={self.curriculum})"

    def __str__(self) -> str:
        return self.name


class Sensei:
    def __init__(self, name: str, start_time: datetime.time, end_time: datetime.time):
        """
        Initializes a Code Ninjas sensei.

        Args:
            name: The name of the sensei.
            start_time: The start time of the class.
            end_time: The end time of the class.
        """

        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return f"Sensei(name={self.name}, start_time={self.start_time}, end_time={self.end_time})"

    def __str__(self) -> str:
        return self.name


class CodeNinjasClass:
    def __init__(
        self,
        start_time: datetime.time,
        end_time: datetime.time = None,
        students: list[Ninja] = None,
        senseis: list[Sensei] = None,
    ):
        """
        Initializes a Code Ninjas class.

        Args:
            start_time: The start time of the class.
            students: The students in the class.
            senseis: The senseis in the class.
        """

        self.start_time = start_time

        if end_time is None:
            end_time = datetime.time(hour=start_time.hour + 1, minute=start_time.minute)
        self.end_time = end_time

        if students is None:
            students = []
        self.students = students

        if senseis is None:
            senseis = []
        self.senseis = senseis

    def __repr__(self) -> str:
        return f"CodeNinjasClass(start_time={self.start_time}, end_time={self.end_time} students={self.students}, senseis={self.senseis})"

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%I')} - {len(self.create_students())} | {len(self.jr_students())}"

    def student_names(self) -> list[str]:
        """
        Returns the names of the students in the class.
        """

        return [student.name for student in self.students]

    def create_students(self) -> list[Ninja]:
        """
        Returns the CREATE students in the class.
        """

        return [student for student in self.students if student.curriculum == Curriculum.CREATE]

    def jr_students(self) -> list[Ninja]:
        """
        Returns the JR students in the class.
        """

        return [student for student in self.students if student.curriculum == Curriculum.JR]

    def unity_students(self, unity_student_names: list[str]) -> list[Ninja]:
        """
        Returns the Unity students in the class.
        """

        return [student for student in self.students if student.name in unity_student_names]

    def focus_students(self, focus_student_names: list[str]) -> list[Ninja]:
        """
        Returns the Focus students in the class.
        """

        return [student for student in self.students if student.name in focus_student_names]

    def sensei_names(self) -> list[str]:
        """
        Returns the names of the senseis in the class.
        """

        return [sensei.name for sensei in self.senseis]


def get_class_from_time(classes: list[CodeNinjasClass], time: datetime.time) -> CodeNinjasClass | None:
    """
    Gets the class with the given start time.

    Args:
        classes: The list of classes to search through.
        time: The start time of the class.

    Returns:
        The class with the given start time.
    """

    return next((code_ninjas_class for code_ninjas_class in classes if code_ninjas_class.start_time == time), None)
