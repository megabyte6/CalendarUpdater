import datetime
from enum import Enum


class Curriculum(Enum):
    CREATE = "CREATE"
    JR = "JR"


class Student:
    def __init__(self, name: str, curriculum: Curriculum):
        """
        Initializes a student.

        Args:
            name: The name of the student.
            curriculum: The curriculum the student is in.
        """

        self.name = name
        self.curriculum = curriculum

    def __repr__(self) -> str:
        return f"Student(name={self.name}, curriculum={self.curriculum})"

    def __str__(self) -> str:
        return self.name


class Instructor:
    def __init__(self, name: str, start_time: datetime.time, end_time: datetime.time):
        """
        Initializes a instructor.

        Args:
            name: The name of the instructor.
            start_time: The start time of the session.
            end_time: The end time of the session.
        """

        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return f"Instructor(name={self.name}, start_time={self.start_time}, end_time={self.end_time})"

    def __str__(self) -> str:
        return self.name


class Session:
    def __init__(
        self,
        start_time: datetime.time,
        end_time: datetime.time = None,
        students: list[Student] = None,
        instructors: list[Instructor] = None,
    ):
        """
        Initializes a session.

        Args:
            start_time: The start time of the session.
            students: The students in the session.
            instructors: The instructors in the session.
        """

        self.start_time = start_time

        if end_time is None:
            end_time = datetime.time(hour=start_time.hour + 1, minute=start_time.minute)
        self.end_time = end_time

        if students is None:
            students = []
        self.students = students

        if instructors is None:
            instructors = []
        self.instructors = instructors

    def __repr__(self) -> str:
        return f"Session(start_time={self.start_time}, end_time={self.end_time} students={self.students}, instructors={self.instructors})"

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%I')} - {len(self.create_students())} | {len(self.jr_students())}"

    def student_names(self) -> list[str]:
        """
        Returns the names of the students in the session.
        """

        return [student.name for student in self.students]

    def create_students(self) -> list[Student]:
        """
        Returns the CREATE students in the session.
        """

        return [student for student in self.students if student.curriculum == Curriculum.CREATE]

    def jr_students(self) -> list[Student]:
        """
        Returns the JR students in the session.
        """

        return [student for student in self.students if student.curriculum == Curriculum.JR]

    def unity_students(self, unity_student_names: list[str]) -> list[Student]:
        """
        Returns the Unity students in the session.
        """

        return [student for student in self.students if student.name in unity_student_names]

    def focus_students(self, focus_student_names: list[str]) -> list[Student]:
        """
        Returns the Focus students in the session.
        """

        return [student for student in self.students if student.name in focus_student_names]

    def instructor_names(self) -> list[str]:
        """
        Returns the names of the instructors in the session.
        """

        return [instructor.name for instructor in self.instructors]

    def is_scheduled(self, instructor: Instructor) -> bool:
        """
        Checks whether the given instructor is scheduled for this session.

        Args:
            instructor: The instructor to check.

        Returns:
            Whether the instructor is scheduled for this session.
        """

        today = datetime.date.today()
        start_time = datetime.datetime.combine(date=today, time=self.start_time)
        end_time = datetime.datetime.combine(date=today, time=self.end_time)
        instructor_start_time = datetime.datetime.combine(date=today, time=instructor.start_time)
        instructor_end_time = datetime.datetime.combine(date=today, time=instructor.end_time)

        return instructor_start_time < end_time and instructor_end_time > start_time


def get_session_from_time(sessions: list[Session], time: datetime.time) -> Session | None:
    """
    Gets the session with the given start time.

    Args:
        sessions: The list of sessions to search through.
        time: The start time of the session.

    Returns:
        The session with the given start time.
    """

    return next((session for session in sessions if session.start_time == time), None)
