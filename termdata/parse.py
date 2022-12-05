import sys
import json


class Course:
    def __init__(self, j, includes=None):
        self.json = j
        if includes is None:
            includes = Includes()
        self.includes = includes

    def set_includes(self, includes):
        self.includes = includes

    def __str__(self):
        return json.dumps(self.includes.slim_json(self.json))

class Includes:
    def __init__(self):
        self.includes = {
            "id": True,
            "term": True,
            "termDesc": True,
            "courseReferenceNumber": True,
            "partOfTerm": False,
            "courseNumber": False,
            "subject": False,
            "subjectDescription": False,
            "sequenceNumber": True,
            "campusDescription": False,
            "scheduleTypeDescription": False,
            "courseTitle": True,
            "creditHours": False,
            "maximumEnrollment": True,
            "enrollment": True,
            "seatsAvailable": True,
            "waitCapacity": True,
            "waitCount": True,
            "waitAvailable": True,
            "crossList": False,
            "crossListCapacity": False,
            "crossListCount": False,
            "crossListAvailable": False,
            "creditHourHigh": True,
            "creditHourLow": True,
            "creditHourIndicator": False,
            "openSection": False,
            "linkIdentifier": False,
            "isSectionLinked": False,
            "subjectCourse": True,
            "faculty": True,
            "meetingsFaculty": False,
            "reservedSeatSummary": False,
            "sectionAttributes": False,
            "instructionalMethod": False,
            "instructionalMethodDescription": True,
        }
        self.faculty_includes = {
            "bannerId": False,
            "category": False,
            "class": False,
            "courseReferenceNumber": False,
            "displayName": True,
            "emailAddress": False,
            "primaryIndicator": False,
            "term": False,
        }
        self.meetings_faculty_includes = {
            "category": False,
            "class": False,
            "courseReferenceNumber": False,
            "faculty": False,
            "meetingTime": True,
            "term": False,
        }
        self.meeting_time_includes = {
            "beginTime": True,
            "building": True,
            "buildingDescription": False,
            "campus": False,
            "campusDescription": True,
            "category": False,
            "class": False,
            "courseReferenceNumber": False,
            "creditHourSession": False,
            "endDate": True,
            "endTime": True,
            "friday": True,
            "hoursWeek": False,
            "meetingScheduleType": False,
            "meetingType": False,
            "meetingTypeDescription": False,
            "monday": True,
            "room": True,
            "saturday": True,
            "startDate": True,
            "sunday": True,
            "term": False,
            "thursday": True,
            "tuesday": True,
            "wednesday": True,
        }

    def pretty_dict(self):
        pretty = {
            "ID": {
                "ID": [self.includes, "id"],
                "CRN": [self.includes, "courseReferenceNumber"],
            },
            "Term": {
                "ID": [self.includes, "term"],
                "Name": [self.includes, "termDesc"],
                "Part": [self.includes, "partOfTerm"],
            },
            "Course": {
                "Campus": [self.includes, "campusDescription"],
                "Subject Code": [self.includes, "subject"],
                "Subject": [self.includes, "subjectDescription"],
                "Course Number": [self.includes, "courseNumber"],
                "Course Code": [self.includes, "subjectCourse"],
                "Course Title": [self.includes, "courseTitle"],
                "Section": [self.includes, "sequenceNumber"],
                "Open Section?": [self.includes, "openSection"],
                "Has Linked Section": [self.includes, "isSectionLinked"],
                "Linked Section": [self.includes, "linkIdentifier"],
                "Instruction Method": [self.includes, "instructionalMethodDescription"],
                "Instruction Method Code": [self.includes, "instructionalMethod"],
                "Section Attributes": [self.includes, "sectionAttributes"],
            },
            "Credits": {
                "Hours": [self.includes, "creditHours"],
                "Hours (Min)": [self.includes, "creditHourLow"],
                "Hours (Max)": [self.includes, "creditHourHigh"],
                "Indicator": [self.includes, "creditHourIndicator"],
            },
            "Enrollment": {
                "Capacity": [self.includes, "maximumEnrollment"],
                "Enrolled": [self.includes, "enrollment"],
                "Available Seats": [self.includes, "seatsAvailable"],
                "Waitlisted": [self.includes, "waitCount"],
                "Waitlist Open": [self.includes, "waitAvailable"],
                "Waitlist Total": [self.includes, "waitCapacity"],
                "Reserved Seats": [self.includes, "reservedSeatSummary"],
            },
            "Cross list": {
                "Course": [self.includes, "crossList"],
                "Capacity": [self.includes, "crossListCapacity"],
                "Enrolled": [self.includes, "crossListCount"],
                "Available Seats": [self.includes, "crossListAvailable"],
            },
            "Faculty": {
                "Name": [self.faculty_includes, "displayName"],
                "Email": [self.faculty_includes, "emailAddress"],
                "Banner ID": [self.faculty_includes, "bannerId"],
                "Is Primary?": [self.faculty_includes, "primaryIndicator"],
                "Term": [self.faculty_includes, "term"],
            },
            "Meeting Time(s)": {
                "Start Date": [self.meeting_time_includes, "startDate"],
                "End Date": [self.meeting_time_includes, "endDate"],
                "Start Time": [self.meeting_time_includes, "beginTime"],
                "End Time": [self.meeting_time_includes, "endTime"],
                "Sunday": [self.meeting_time_includes, "sunday"],
                "Monday": [self.meeting_time_includes, "monday"],
                "Tuesday": [self.meeting_time_includes, "tuesday"],
                "Wednesday": [self.meeting_time_includes, "wednesday"],
                "Thursday": [self.meeting_time_includes, "thursday"],
                "Friday": [self.meeting_time_includes, "friday"],
                "Saturday": [self.meeting_time_includes, "saturday"],
                "Campus Code": [self.meeting_time_includes, "campus"],
                "Campus": [self.meeting_time_includes, "campusDescription"],
                "Building Code": [self.meeting_time_includes, "building"],
                "Building": [self.meeting_time_includes, "buildingDescription"],
                "Room": [self.meeting_time_includes, "room"],
                "Schedule Type": [self.meeting_time_includes, "meetingScheduleType"],
                "Schedule Type Description": [self.includes, "scheduleTypeDescription"],
                "Type": [self.meeting_time_includes, "meetingType"],
                "Type Description": [self.meeting_time_includes, "meetingTypeDescription"],
                "Credit Hour Session": [self.meeting_time_includes, "creditHourSession"],
                "Hours per Week": [self.meeting_time_includes, "hoursWeek"],
            }
        }
        return pretty

    def view_example(self, view_all=False):
        pretty_dict = self.pretty_dict()
        example_section = {"id": 643201, "term": "202240", "termDesc": "Fall 2022", "courseReferenceNumber": "40025", "partOfTerm": "1", "courseNumber": "2010", "subject": "ACCT", "subjectDescription": "Accounting", "sequenceNumber": "001", "campusDescription": "Logan Main Campus", "scheduleTypeDescription": "Face to Face Lecture", "courseTitle": "Financial Accounting Principles", "creditHours": None, "maximumEnrollment": 79, "enrollment": 47, "seatsAvailable": 32, "waitCapacity": 100, "waitCount": 0, "waitAvailable": 100, "crossList": None, "crossListCapacity": None, "crossListCount": None, "crossListAvailable": None, "creditHourHigh": None, "creditHourLow": 3, "creditHourIndicator": None, "openSection": True, "linkIdentifier": None, "isSectionLinked": False, "subjectCourse": "ACCT2010", "faculty": [{"bannerId": "284715", "category": None, "class": "net.hedtech.banner.student.faculty.FacultyResultDecorator", "courseReferenceNumber": "40025", "displayName": "Paul Campbell", "emailAddress": "paul.campbell@usu.edu", "primaryIndicator": True, "term": "202240"}], "meetingsFaculty": [{"category": "01", "class": "net.hedtech.banner.student.schedule.SectionSessionDecorator", "courseReferenceNumber": "40025", "faculty": [], "meetingTime": {"beginTime": "0730", "building": "HH", "buildingDescription": "Huntsman Hall", "campus": "M", "campusDescription": "Logan Main Campus", "category": "01", "class": "net.hedtech.banner.general.overall.MeetingTimeDecorator", "courseReferenceNumber": "40025", "creditHourSession": 3.0, "endDate": "12/16/2022", "endTime": "0845", "friday": False, "hoursWeek": 2.5, "meetingScheduleType": "LEC", "meetingType": "CLAS", "meetingTypeDescription": "Class", "monday": True, "room": "220", "saturday": False, "startDate": "08/29/2022", "sunday": False, "term": "202240", "thursday": False, "tuesday": False, "wednesday": True}, "term": "202240"}], "reservedSeatSummary": None, "sectionAttributes": None, "instructionalMethod": "P", "instructionalMethodDescription": "Face-to-Face"}
        for category, items in pretty_dict.items():
            print(category)
            for k, v in items.items():
                if v[0][v[1]] or view_all:
                    print("\t" + k)
                    if v[0] is self.includes:
                        print("\t\t" + example_section[v[1]])
                    elif v[0] is self.faculty_includes:
                        print("\t\t" + example_section["faculty"][v[1]])
                    elif v[0] is self.meeting_time_includes:
                        print("\t\t" + example_section["meetingsFaculty"]["meetingTime"][v[1]])

    def slim_json(self, j):
        new_j = {}
        for k, v in j.items():
            if self.includes[k]:
                if k == "faculty":
                    new_f = []
                    for faculty in v:
                        new_faculty = {}
                        for k2, v2 in faculty.items():
                            if self.faculty_includes[k2]:
                                new_faculty[k2] = v2
                        new_f.append(new_faculty)
                    new_j[k] = new_f
                elif k == "meetingsFaculty":
                    new_mf = []
                    for meeting_faculty in v:
                        new_meeting_faculty = {}
                        for k2, v2 in meeting_faculty.items():
                            if self.meeting_faculty_includes[k2]:
                                if k2 == "meetingTime":
                                    new_mt = {}
                                    for k3, v3 in v2.items():
                                        if self.meeting_time_includes[k3]:
                                            new_mt[k3] = v3
                                    new_meeting_faculty[k2] = new_mt
                                else:
                                    new_meeting_faculty[k2] = v2
                        new_mf.append(new_meeting_faculty)
                    new_j[k] = new_mf
                else:
                    new_j[k] = v
        return new_j


if __name__ == "__main__":
    args = sys.argv
    courses = []
    for arg in args[1:-1]:
        f = open(arg, 'r')
        s = f.read()
        f.close()
        for j in json.loads(s):
            course = Course(j)
            courses.append(str(course))
    f = open(args[-1], 'x')
    f.write("[" + ",".join(courses) + "]")
    f.close()

