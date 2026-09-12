from kivy.app import App
from backend.constants import (
    REQUIRED_ATTENDANCE,
    HOLIDAYS,
    NO_INSTRUCTION_START,
    NO_INSTRUCTION_END,
    MIDSEM_START,
    MIDSEM_END,
    ENDSEM_START,
    ENDSEM_END,
    SEMESTER_START,
    LAST_FORMAL_TEACHING,
)
from backend.storage import (
    get_slot_entry,
    cancellation_key,
    load_cancellations,
)


def get_slot_subject(day, index):
    return get_slot_entry(day, index).get("subject", "")


def get_slot_type(day, index):
    return get_slot_entry(day, index).get("type", "")


def is_class_cancelled(class_date, subject, time):
    app = App.get_running_app()
    cancellations = getattr(app, "cancellations_data", None)
    if cancellations is None:
        cancellations = load_cancellations()
    return cancellation_key(class_date, subject, time) in cancellations


def get_semester_status(class_date):
    if class_date in HOLIDAYS:
        return HOLIDAYS[class_date]

    if NO_INSTRUCTION_START <= class_date <= NO_INSTRUCTION_END:
        return "NO INSTRUCTION"

    if MIDSEM_START <= class_date <= MIDSEM_END:
        return "MID-SEM EXAM"

    if ENDSEM_START <= class_date <= ENDSEM_END:
        return "END-SEM EXAM"

    if class_date < SEMESTER_START:
        return "SEMESTER NOT STARTED"

    if class_date > LAST_FORMAL_TEACHING:
        return "TEACHING ENDED"

    return None


def get_subject_stats(subject, class_type=None):
    data = App.get_running_app().attendance_data

    present = 0
    absent = 0

    for record in data.values():
        if record.get("subject") != subject:
            continue
        record_type = str(record.get("type", "LECTURE") or "LECTURE").upper()
        if class_type and record_type != class_type.upper():
            continue

        if record.get("status") == "present":
            present += 1
        elif record.get("status") == "absent":
            absent += 1

    total = present + absent

    if total == 0:
        percentage = None
    else:
        percentage = (present / total) * 100

    return present, absent, total, percentage


def get_type_stats(class_type):
    data = App.get_running_app().attendance_data
    present = 0
    absent = 0
    wanted = class_type.upper()

    for record in data.values():
        record_type = str(record.get("type", "LECTURE") or "LECTURE").upper()
        if record_type != wanted:
            continue
        if record.get("status") == "present":
            present += 1
        elif record.get("status") == "absent":
            absent += 1

    total = present + absent
    percentage = (present / total * 100) if total else None
    return present, absent, total, percentage


def classes_can_skip(present, total):
    if total == 0:
        return 0

    skipped = 0
    while True:
        future_total = total + skipped + 1
        future_present = present
        future_percentage = (future_present / future_total) * 100
        if future_percentage >= REQUIRED_ATTENDANCE:
            skipped += 1
        else:
            break

    return skipped

