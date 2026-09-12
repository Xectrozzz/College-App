from datetime import date

REQUIRED_ATTENDANCE = 75

TIMES = [
    "8:00 - 8:55",
    "9:00 - 9:55",
    "10:00 - 10:55",
    "11:00 - 11:55",
    "12:00 - 12:55",
    "1:00 - 1:55",
    "2:00 - 3:55",
    "4:00 - 6:00"
]

TIMETABLE = {
    "MONDAY": [
        "MATHEMATICS",
        "",
        "",
        "ENGLISH & CORPORATE COMMUNICATION",
        "ENGLISH & CORPORATE COMMUNICATION",
        "LUNCH BREAK",
        "GRAPHICS - I",
        "GRAPHICS - I"
    ],
    "TUESDAY": [
        "",
        "MATHEMATICS",
        "",
        "MATERIALS & CONSTRUCTION - I",
        "HISTORY OF ARCHITECTURE - I",
        "LUNCH BREAK",
        "BASIC DESIGN & VISUAL ARTS",
        "BASIC DESIGN & VISUAL ARTS"
    ],
    "WEDNESDAY": [
        "",
        "",
        "",
        "MATERIALS & CONSTRUCTION - I",
        "HISTORY OF ARCHITECTURE - I",
        "LUNCH BREAK",
        "MATERIALS & CONSTRUCTION - I",
        "MATERIALS & CONSTRUCTION - I"
    ],
    "THURSDAY": [
        "",
        "",
        "ENGLISH & CORPORATE COMMUNICATION",
        "MATHEMATICS",
        "",
        "LUNCH BREAK",
        "BASIC DESIGN & VISUAL ARTS",
        ""
    ],
    "FRIDAY": [
        "",
        "HISTORY OF ARCHITECTURE - I",
        "ENGLISH & CORPORATE COMMUNICATION",
        "HISTORY OF ARCHITECTURE - I",
        "",
        "LUNCH BREAK",
        "",
        "SPORTS - I"
    ]
}

SUBJECTS = [
    "MATHEMATICS",
    "ENGLISH & CORPORATE COMMUNICATION",
    "MATERIALS & CONSTRUCTION - I",
    "HISTORY OF ARCHITECTURE - I",
    "GRAPHICS - I",
    "BASIC DESIGN & VISUAL ARTS",
    "SPORTS - I"
]

CLASS_TYPES = ["LECTURE", "TUTORIAL", "PRACTICAL", "STUDIO"]

SUBJECT_INFO = {
    "MATHEMATICS": {
        "credits": 3,
        "teacher": "",
        "syllabus": [
            "Three Dimensional Geometry: Directional cosines and ratios, angle between two lines, equations of straight lines, coplanar lines, equation of plane, shortest distance between lines and planes, sphere, tangent plane, and plane section of a sphere.",
            "Matrices and Linear Programming: Inverse of a square matrix using adjoint matrix, rank of a matrix, elementary row and column transformations, Gauss elimination, consistency and inconsistency of linear equations, formulation of LPP, graphical method, and simplex method.",
            "Statistics: Measures of central tendency (arithmetic mean, median, mode), measures of dispersion (standard deviation and variance), regression and correlation, and curve fitting by least squares for a straight line and parabola.",
            "Calculus: Tangent and normal, maxima and minima of functions of one variable, curvature, Taylor's and Maclaurin's expansion, reduction formulae, and calculation of area using integrals (arc length and area under a curve)."
        ]
    },
    "ENGLISH & CORPORATE COMMUNICATION": {
        "credits": 3,
        "teacher": "",
        "syllabus": [
            "Introduction to Communication: Principles of communication, channels of communication, inclusive communication practices, speaking and listening skills.",
            "Introduction to Corporate Communication: Different forms of corporate communication, factors influencing corporate communication, interpersonal communication, and communication for effective leadership.",
            "Verbal and Non-verbal Communication: Reading and writing skills for corporate communication, nonverbal communication in corporate settings, interviews and group discussions, and presentation skills.",
            "Features of Corporate Communication: Levels of corporate communication, barriers to communication, organizational communication, and dos and don'ts of corporate communication.",
            "Strategies of Communication: Negotiating conflict and management, crisis communication, emotional intelligence and stress management, and ethics in corporate communication.",
            "Indicative activities: Ice breaker, oral presentation, listening activity, role play, group discussion, writing activities, peer interview, PPT presentation, debate, corporate meeting, case study, and interviewing strangers."
        ]
    },
    "MATERIALS & CONSTRUCTION - I": {
        "credits": 4,
        "teacher": "",
        "syllabus": [
            "Building Materials Overview: Types, properties, uses, standards, composition, and application of basic building materials such as brick, stone, binding materials, and mortar.",
            "Building Elements and Structural Systems: Components from foundation to roof and a general idea of load transmission in load-bearing and framed structures, including their advantages, disadvantages, and suitability.",
            "Foundation Types and Construction Details: Various types of foundation with emphasis on load-bearing walls, plinth filling, steps, and related construction details.",
            "Masonry Construction Techniques: Brick and stone masonry including walls, piers, staircases, roofs, domes, and types of bonds such as English and Flemish bonds.",
            "Architectural Supports and Construction Tools: Introduction to lintels and arches and to basic tools and equipment used in construction."
        ]
    },
    "HISTORY OF ARCHITECTURE - I": {
        "credits": 4,
        "teacher": "",
        "syllabus": [
            "Understanding Early Settlements and Architecture Across Cultures (2600 BCE – 500 BCE): Indus Valley Civilization, early Aryan architecture of the Ganga Basin, and Vedic principles of planning including Vastu Purusha Mandala, cardinal orientation, and cosmic order.",
            "Architecture of Ancient Civilizations (3000 BCE – 400 CE): Egypt, Mesopotamia, Persia, Greece, and Rome, including their construction techniques, architectural typologies, structural systems, monuments, and symbolic significance.",
            "Inception and Development of Buddhist Architecture in India and Abroad (500 BCE – 1200 CE): Stupas, viharas, chaityas, rock-cut architecture, Southeast Asian adaptations, Chinese and Japanese wooden architecture, and the spread of forms through the Silk Route.",
            "Development of Hindu Temple Architecture (200 BCE – 1300 CE): Vedic and Buddhist planning influences, garbhagriha, regional Nagara, Dravida and Vesara styles, temple towns, stepwells, and the spread of Hindu architecture abroad."
        ]
    },
    "GRAPHICS - I": {
        "credits": 2,
        "teacher": "",
        "syllabus": [
            "Introduction to architectural drafting techniques, lettering, and use of drawing instruments.",
            "Scale construction (plain and diagonal) and 2D drawings in reduced and enlarged scales.",
            "Orthographic projections of points, lines, planes, and solids with reference to HP and VP; simple compositions in plan and elevation.",
            "Sections and true sections of solids in various positions and surface development of standard solids.",
            "Isometric and axonometric projections of solids and building elements using isometric scale.",
            "Graphical symbols for materials, furniture, and services; presentation drawings with rendering and line quality.",
            "Intersections and interpenetration of solids; complex sections and development of composite 3D forms."
        ]
    },
    "BASIC DESIGN & VISUAL ARTS": {
        "credits": 9,
        "teacher": "",
        "syllabus": [
            "Introduction to Design/Visual Arts and related terminologies and concepts.",
            "Elements of Design: Properties, qualities, and characteristics of point, line, direction, plane, shape, form, color, texture, space, light, and shadow.",
            "Principles of Design: Scale, proportion, balance, harmony, rhythm, contrast, and related principles.",
            "Compositions: Application of design elements and principles in two-dimensional and three-dimensional compositions.",
            "Expression in Art and Architecture: Expression in performing and visual arts and architecture with social components.",
            "Visual Appraisal: Evaluation of design forms for visual character, interplay of light and shadow, solids and voids, spatial temperature, and material qualities.",
            "Interdisciplinary Connections: Allied visual and performing arts and their relationship to the built environment."
        ]
    },
    "SPORTS - I": {
        "credits": 0,
        "teacher": "",
        "syllabus": [
            "The supplied 2025 B.Arch syllabus PDF lists SAA101 Health Information & Sports-I as a Semester I course with 0 credits and 2 practical hours, but does not provide a detailed course-syllabus section for it in the supplied document."
        ]
    }
}

SEMESTER_START = date(2026, 8, 24)
LAST_FORMAL_TEACHING = date(2026, 12, 5)

MIDSEM_START = date(2026, 10, 1)
MIDSEM_END = date(2026, 10, 10)

ENDSEM_START = date(2026, 12, 7)
ENDSEM_END = date(2026, 12, 15)

NO_INSTRUCTION_START = date(2026, 11, 9)
NO_INSTRUCTION_END = date(2026, 11, 13)

HOLIDAYS = {
    date(2026, 8, 26): "HOLIDAY\nId-e-Milad",
    date(2026, 10, 2): "HOLIDAY\nMahatma Gandhi Birthday",
    date(2026, 10, 20): "HOLIDAY\nDussehra",
    date(2026, 11, 8): "HOLIDAY\nDiwali",
    date(2026, 11, 24): "HOLIDAY\nGuru Nanak Birthday",
    date(2026, 12, 25): "HOLIDAY\nChristmas Day",
    date(2027, 1, 26): "HOLIDAY\nRepublic Day",
}

SPECIAL_SATURDAYS = {
    date(2026, 8, 29): "MONDAY",
    date(2026, 9, 5): "TUESDAY",
    date(2026, 9, 12): "WEDNESDAY",
    date(2026, 9, 19): "THURSDAY",
    date(2026, 9, 26): "FRIDAY",
    date(2026, 10, 17): "MONDAY",
    date(2026, 10, 24): "TUESDAY",
    date(2026, 10, 31): "WEDNESDAY",
    date(2026, 11, 21): "THURSDAY",
    date(2026, 11, 28): "TUESDAY",
    date(2026, 12, 5): "TUESDAY",
}

