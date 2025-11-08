# ruff: noqa: E501

from models.base import Course, CourseID


# Our synthetic courses, including their basic info
COURSES = [
    Course(
        id=CourseID.MAT901,
        name="Introduction to Probability and Statistics",
        description="This course covers the basic principles of probability and statistics. Topics include probability rules, random variables, common distributions (like binomial and normal), sampling, confidence intervals, and hypothesis testing. Students learn to analyse data and interpret results using real-world examples.",
        n_lectures=10,
        syllabus_url="https://campusdata.blob.core.windows.net/synthetic-data/syllabus_MAT901.md",
        exam_url="https://campusdata.blob.core.windows.net/synthetic-data/exam_MAT901.json",
    ),
    Course(
        id=CourseID.ECO901,
        name="Macroeconomics: Growth and Fluctuations",
        description="This course introduces students to key concepts in macroeconomics. It covers topics like GDP, inflation, unemployment, economic growth, and business cycles. Students learn how government policies affect the economy and explore basic models used to explain economic trends.",
        n_lectures=10,
        syllabus_url="https://campusdata.blob.core.windows.net/synthetic-data/syllabus_ECO901.md",
        exam_url="https://campusdata.blob.core.windows.net/synthetic-data/exam_ECO901.json",
    ),
    Course(
        id=CourseID.LAW901,
        name="Law and Society: Foundations of Public Law",
        description="This course provides an introduction to public law and its role in society. Students learn about the constitution, separation of powers, the role of courts, and fundamental rights. Real-world cases help illustrate how public law shapes and protects democratic institutions.",
        n_lectures=10,
        syllabus_url="https://campusdata.blob.core.windows.net/synthetic-data/syllabus_LAW901.md",
        exam_url="https://campusdata.blob.core.windows.net/synthetic-data/exam_LAW901.json",
    ),
    Course(
        id=CourseID.FIN901,
        name="Principles of Financial Literacy",
        description="This course introduces key concepts in personal and corporate finance. Students explore topics such as budgeting, saving, interest rates, investing, and financial decision-making. The course also covers financial institutions and tools used to manage risk and build financial security.",
        n_lectures=10,
        syllabus_url="https://campusdata.blob.core.windows.net/synthetic-data/syllabus_FIN901.md",
        exam_url="https://campusdata.blob.core.windows.net/synthetic-data/exam_FIN901.json",
    ),
    # The following course is not generated, and truly exists. It is mostly used for evaluation purposes
    Course(
        id=CourseID.PYT101,
        name="Introduction to Programming with Python for Computational Science",
        description="This course teaches the basics of programming using Python. Students learn fundamental concepts such as variables, data types, loops, conditionals, functions, classes, and simple data structures like lists and dictionaries. Through hands-on exercises oriented for computational science, they gain practical experience in solving problems and writing clean, efficient code.",
        n_lectures=4,
        syllabus_url="https://campusdata.blob.core.windows.net/synthetic-data/syllabus_PYT101.md",
        exam_url="https://campusdata.blob.core.windows.net/synthetic-data/exam_PYT101.json",
    ),
]

COURSES = {course.id: course for course in COURSES}
