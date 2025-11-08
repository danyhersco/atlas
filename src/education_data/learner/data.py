# ruff: noqa: E501

from models.base import Learner, CourseID, LearnerLevel


LEARNER_ID_TO_COURSE_ID = {
    # Evaluation Students
    "learner_1": [CourseID.PYT101],
    "learner_2": [CourseID.PYT101],
    "learner_3": [CourseID.PYT101],
    "learner_4": [CourseID.PYT101],
    "learner_5": [CourseID.PYT101],
    "learner_6": [CourseID.PYT101],
    "learner_7": [CourseID.PYT101],
    "learner_8": [CourseID.PYT101],
    "learner_9": [CourseID.PYT101],
    # Demo Student
    "learner_10": [
        CourseID.PYT101,
        CourseID.MAT901,
        CourseID.ECO901,
        CourseID.FIN901,
        CourseID.LAW901,
    ],
}

# Our synthetic learners, including their basic info
LEARNERS = [
    Learner(
        id="learner_1",
        name="Noah Patel",
        programme="BEng Mechanical Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_1"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_1"]
        },
        level=LearnerLevel.BEGINNER,
    ),
    Learner(
        id="learner_2",
        name="Maya Okafor",
        programme="BSc Electrical and Computer Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_2"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_2"]
        },
        level=LearnerLevel.BEGINNER,
    ),
    Learner(
        id="learner_3",
        name="Liam Chen",
        programme="BSc Software Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_3"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_3"]
        },
        level=LearnerLevel.BEGINNER,
    ),
    Learner(
        id="learner_4",
        name="Zara Al-Mansouri",
        programme="BEng Aerospace Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_4"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_4"]
        },
        level=LearnerLevel.INTERMEDIATE,
    ),
    Learner(
        id="learner_5",
        name="Ethan Rossi",
        programme="BSc Civil and Environmental Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_5"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_5"]
        },
        level=LearnerLevel.INTERMEDIATE,
    ),
    Learner(
        id="learner_6",
        name="Priya Nair",
        programme="BSc Biomedical Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_6"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_6"]
        },
        level=LearnerLevel.INTERMEDIATE,
    ),
    Learner(
        id="learner_7",
        name="Diego Alvarez",
        programme="BEng Chemical Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_7"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_7"]
        },
        level=LearnerLevel.ADVANCED,
    ),
    Learner(
        id="learner_8",
        name="Aisha Khan",
        programme="BSc Data Science and AI Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_8"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_8"]
        },
        level=LearnerLevel.ADVANCED,
    ),
    Learner(
        id="learner_9",
        name="Jonas Müller",
        programme="BSc Computer Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_9"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_9"]
        },
        level=LearnerLevel.ADVANCED,
    ),
    Learner(
        id="learner_10",
        name="Dany Herscovitch",
        programme="MSc Applied Computational Science and Engineering",
        course_ids=LEARNER_ID_TO_COURSE_ID["learner_10"],
        learning_preferences={
            cid: [] for cid in LEARNER_ID_TO_COURSE_ID["learner_10"]
        },
        # no level here as this learner is for Demo purpose
    ),
]

LEARNERS = {learner.id: learner for learner in LEARNERS}
