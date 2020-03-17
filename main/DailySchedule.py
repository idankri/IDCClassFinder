import json
from datetime import datetime


# DATA = r"C:\Users\User\Documents\Projects\IDCClassFinder\main\data.json"


class DailySchedule(object):
    def __init__(self, classroom, day, schedule):
        self.classroom = classroom
        self.day = int(day)
        self.lecture_schedule = []
        for lecture in schedule:
            self.lecture_schedule.append(TimeSlot.from_string(lecture, self.day))

    def vacant_hours(self, gap=60, specific_time="20:00 - 8:00"):
        """
        Creates a list of all the vacant hours for a specific classroom and a specific day.
        :param gap: the requested gap between lectures. in minutes.
        :param specific_time: an option to give a specific time frame.
                              the list will contain only gaps that are within the time frame.
                              the time frame will be passed as a string in the known format.
        :return: the list.
        """
        gap_in_minutes = gap * 60
        time_frame = TimeSlot.from_string(specific_time, self.day)
        ans = []

        # check the beginning of the day
        first_delta = self.lecture_schedule[0].start - time_frame.start
        if first_delta.days == 0 and first_delta.seconds >= gap_in_minutes:
            ans.append(TimeSlot.from_datetime(time_frame.start, self.lecture_schedule[0].start))

        # check for time gaps during the day
        for i in range(len(self.lecture_schedule) - 1):
            start_delta = self.lecture_schedule[i + 1].start - time_frame.start
            end_delta = time_frame.end - self.lecture_schedule[i].end
            if (start_delta.days == 0 and start_delta.seconds != 0) and (
                    end_delta.days == 0 and end_delta.seconds != 0):
                delta = self.lecture_schedule[i + 1].start - self.lecture_schedule[i].end
                if delta.seconds >= gap_in_minutes:
                    ans.append(TimeSlot.from_datetime(self.lecture_schedule[i].end, self.lecture_schedule[i + 1].start))

        # check the end of the day
        last_delta = time_frame.end - self.lecture_schedule[-1].end
        if last_delta.days == 0 and last_delta.seconds >= gap_in_minutes:
            ans.append(TimeSlot.from_datetime(self.lecture_schedule[-1].end, time_frame.end))
        return ans


def parse_start(lecture_hours, day):
    """
    Extract from the string the lecture's start time and parse it into a datetime object.
    :param lecture_hours: the string that contains the lecture's hours.
    :param day: the day of the week of which the lecture takes place.
    :return: a datetime object that holds the time that the lecture starts at.
    """
    if lecture_hours[-5] == ' ':
        return datetime(2020, 3, day, int(lecture_hours[-4:-3]), int(lecture_hours[-2:]))
    return datetime(2020, 3, day, int(lecture_hours[-5:-3]), int(lecture_hours[-2:]))


def parse_end(lecture_hours, day):
    """
    Extract from the string the lecture's end time and parse it into a datetime object.
    :param lecture_hours: the string that contains the lecture's hours.
    :param day: the day of the week of which the lecture takes place.
    :return: a datetime object that holds the time that the lecture ends at.
    """
    if lecture_hours[1] == ':':
        return datetime(2020, 3, day, int(lecture_hours[:1]), int(lecture_hours[2:4]))
    return datetime(2020, 3, day, int(lecture_hours[:2]), int(lecture_hours[3:5]))


class TimeSlot(object):
    def __init__(self, start, end, duration):
        self.start = start
        self.end = end
        self.duration = duration

    @classmethod
    def from_string(cls, time_string, day):
        """
        Creates a TimeSlot object from a specific format of a string.
        :param time_string: the string.
        :param day: the day of which the lecture takes place.
        :return: a TimeSlot object that holds the lecture's hours.
        """
        start = parse_start(time_string, day)
        end = parse_end(time_string, day)
        duration = end - start
        return cls(start, end, duration)

    @classmethod
    def from_datetime(cls, start_time, end_time):
        """
        Creates a TimeSlot object from two datetime objects.
        :param start_time: a datetime object of the beginning of the period.
        :param end_time: a datetime object of the end of the period.
        :return: a TimeSlot object that holds the lecture's hours.
        """
        return cls(start_time, end_time, end_time - start_time)


def parse_data(path):
    with open(path, 'r') as file:
        data = json.load(file)
    for classroom in data.keys():
        days = data[classroom]
        for day in days:
            days[day] = DailySchedule(classroom, day, days[day])
    return data


def lectures_per_class_and_day(classroom_dict, classroom, day):
    """
    Gets the lecture schedule of a specific classroom in a specific day
    :return: the classroom's lecture schedule for the day
    """
    print("The lecture schedule for {} for day {} is:".format(classroom, day))
    for lecture in classroom_dict[classroom][day].lecture_schedule:
        print(lecture.start.time(), lecture.end.time(), lecture.duration)


def vacancies_per_class_and_day(classroom_dict, classroom, day, gap=60, time_frame="20:00 - 8:00"):
    """
    Gets the vacant times of a specific classroom in a specific day
    :return: the classroom's vacant times for the day
    """
    vacant = classroom_dict[classroom][day].vacant_hours(gap, time_frame)
    print("The vacant hours for {} for day {} for the requested time gap and time frame are:".format(classroom, day))
    for slot in vacant:
        print(slot.start.time(), slot.end.time(), slot.duration)



