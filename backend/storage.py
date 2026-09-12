import json
import os
from datetime import date
from kivy.app import App
from backend.constants import TIMES, TIMETABLE, CLASS_TYPES, SPECIAL_SATURDAYS, SUBJECT_INFO


def get_timetable_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "timetable.json")


def _default_timetable_data():
    """Convert the original timetable into the user-editable format."""
    data = {}
    for day, slots in TIMETABLE.items():
        data[day] = []
        for subject in slots:
            if subject and subject != "LUNCH BREAK":
                data[day].append({"subject": subject, "type": "LECTURE"})
            elif subject == "LUNCH BREAK":
                data[day].append({"subject": "LUNCH BREAK", "type": ""})
            else:
                data[day].append({"subject": "", "type": ""})
    return data


def _normalise_timetable(data):
    """Accept both old string format and new slot-object format."""
    result = {}
    defaults = _default_timetable_data()
    for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"):
        raw_slots = data.get(day, defaults.get(day, [])) if isinstance(data, dict) else []
        result[day] = []
        for index in range(len(TIMES)):
            value = raw_slots[index] if index < len(raw_slots) else {"subject": "", "type": ""}
            if isinstance(value, str):
                subject = value
                class_type = "LECTURE" if subject and subject != "LUNCH BREAK" else ""
                result[day].append({"subject": subject, "type": class_type})
            elif isinstance(value, dict):
                subject = str(value.get("subject", "") or "")
                class_type = str(value.get("type", "") or "").upper()
                if subject and subject != "LUNCH BREAK":
                    if class_type not in CLASS_TYPES:
                        class_type = "LECTURE"
                else:
                    class_type = ""
                result[day].append({"subject": subject, "type": class_type})
            else:
                result[day].append({"subject": "", "type": ""})
    return result


def load_timetable():
    filename = get_timetable_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
            normalised = _normalise_timetable(data)
            if data != normalised:
                save_timetable(normalised)
            return normalised
    except Exception as e:
        print("Could not load timetable:", e)

    data = _default_timetable_data()
    try:
        save_timetable(data)
    except Exception:
        pass
    return data


def save_timetable(data):
    filename = get_timetable_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(_normalise_timetable(data), file, indent=4)
        app = App.get_running_app()
        if app is not None:
            app.timetable_data = _normalise_timetable(data)
    except Exception as e:
        print("Could not save timetable:", e)


def get_timetable():
    app = App.get_running_app()
    data = getattr(app, "timetable_data", None)
    if data is None:
        data = load_timetable()
        if app is not None:
            app.timetable_data = data
    return data


def get_slot_entry(day, index):
    timetable = get_timetable()
    slots = timetable.get(day, [])
    if index < len(slots):
        value = slots[index]
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return {
                "subject": value,
                "type": "LECTURE" if value and value != "LUNCH BREAK" else ""
            }
    return {"subject": "", "type": ""}


def get_teacher_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "teachers.json")


def load_teachers():
    filename = get_teacher_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
    except Exception as e:
        print("Could not load teachers:", e)
    return {}


def save_teachers(data):
    filename = get_teacher_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Could not save teachers:", e)


def get_teacher(subject):
    saved = load_teachers()
    return saved.get(subject, SUBJECT_INFO.get(subject, {}).get("teacher", ""))


def get_subject_prep_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "subject_prep.json")


def load_subject_prep():
    filename = get_subject_prep_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
    except Exception as e:
        print("Could not load subject prep:", e)
    return {}


def save_subject_prep(data):
    filename = get_subject_prep_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Could not save subject prep:", e)


def get_subject_prep(subject):
    data = load_subject_prep()
    item = data.get(subject, {})
    return item if isinstance(item, dict) else {}


def save_subject_prep_for_subject(subject, what_to_bring, notes):
    data = load_subject_prep()
    data[subject] = {
        "what_to_bring": what_to_bring.strip(),
        "notes": notes.strip(),
    }
    save_subject_prep(data)


def get_subject_assignments(subject):
    app = App.get_running_app()
    filename = os.path.join(app.user_data_dir, "assignments.json")
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                assignments = json.load(file)
                if isinstance(assignments, list):
                    return [
                        item for item in assignments
                        if item.get("subject") == subject
                    ]
    except Exception as e:
        print("Could not load subject assignments:", e)
    return []


def get_cancellation_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "cancellations.json")


def cancellation_key(class_date, subject, time):
    return f"{class_date}|{subject}|{time}"


def load_cancellations():
    filename = get_cancellation_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
    except Exception as e:
        print("Could not load cancellations:", e)
    return {}


def save_cancellations(data):
    filename = get_cancellation_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        app = App.get_running_app()
        if app is not None:
            app.cancellations_data = data
    except Exception as e:
        print("Could not save cancellations:", e)


def get_attendance_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "attendance.json")


def attendance_key(class_date, subject, time, class_type=None):
    base = f"{class_date}|{subject}|{time}"
    if class_type:
        return f"{base}|{str(class_type).upper()}"
    return base


def infer_attendance_type(record):
    current_type = str(record.get("type", "") or "").upper()
    if current_type in CLASS_TYPES and current_type != "LECTURE":
        return current_type

    try:
        class_date = date.fromisoformat(str(record.get("date", "")))
        time = record.get("time", "")
        subject = record.get("subject", "")
        if time not in TIMES or not subject:
            return current_type or "LECTURE"

        weekday = class_date.strftime("%A").upper()
        if weekday == "SUNDAY":
            return current_type or "LECTURE"
        timetable_day = (
            SPECIAL_SATURDAYS.get(class_date)
            if weekday == "SATURDAY"
            else weekday
        )
        if timetable_day:
            index = TIMES.index(time)
            slot = get_slot_entry(timetable_day, index)
            if slot.get("subject") == subject:
                slot_type = str(slot.get("type", "") or "").upper()
                if slot_type in CLASS_TYPES:
                    return slot_type
    except Exception:
        pass

    return current_type or "LECTURE"


def load_attendance():
    filename = get_attendance_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
            migrated = {}
            changed = False
            if isinstance(data, dict):
                for old_key, record in data.items():
                    if not isinstance(record, dict):
                        continue
                    record = dict(record)
                    class_type = infer_attendance_type(record)
                    record["type"] = class_type
                    new_key = attendance_key(
                        record.get("date", ""),
                        record.get("subject", ""),
                        record.get("time", ""),
                        class_type,
                    )
                    migrated[new_key] = record
                    if old_key != new_key or record != data.get(old_key):
                        changed = True

            if changed or migrated != data:
                save_attendance(migrated)
                return migrated
            return data

    except Exception:
        pass

    return {}


def save_attendance(data):
    filename = get_attendance_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Could not save attendance:", e)
