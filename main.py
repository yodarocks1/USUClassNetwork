import json
import networkx as nx
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class Enrollment:
    def __init__(self, enrollment, enrollment_max, enrollment_available):
        if int(enrollment_max) - int(enrollment) != int(enrollment_available):
            raise ValueError("")
        self.enrollment = enrollment
        self.enrollment_max = enrollment_max
    def filled(self):
        return self.enrollment
    def max(self):
        return self.enrollment_max
    def available(self):
        return self.enrollment_max - self.enrollment
    def percentage(self):
        return self.enrollment / self.enrollment_max

def program_to_data_dict(program):
    return {
        "desc": program["desc"],
        "college": program["college"],
        "department": program["department"]
    }

def course_to_data_dict(course):
    return {
        "coid": course["courseID"],
        "desc": course["desc"]
    }

def section_to_data_dict(section):
    return {
        "crn": section["courseReferenceNumber"],
        "section": section["sequenceNumber"],
        "desc": section["courseTitle"],
        "enrollment": Enrollment(section["enrollment"], section["maximumEnrollment"], section["seatsAvailable"]),
        "waitlist": Enrollment(section["waitCount"], section["waitCapacity"], section["waitAvailable"]),
        "credits": [section["creditHourLow"], section["creditHourHigh"]],
        "course": section["subjectCourse"],
        "faculty": list(map(lambda f: f["displayName"], section["faculty"])),
        "method": section["instructionalMethodDescription"]
    }

def section_course_to_course(section_course):
    return " ".join(re.findall(r"[^\W\d_]+|\d+", section_course))

def course_id_map(courses):
    id_map = {}
    for course in courses:
        id_map[course["courseID"]] = course["subNum"]
    return id_map

def create_graphs():
    f = open("programsData/programs_all.json")
    programs = json.load(f)
    f.close()
    f = open("coursesData/courses_all.json")
    courses = json.load(f)
    f.close()
    f = open("termdata/202240slim.json")
    term2022f = json.load(f)
    f.close()
    f = open("termdata/202320slim.json")
    term2023s = json.load(f)
    f.close()

    course_map = course_id_map(courses)
    
    g2022f = nx.Graph()
    g2023s = nx.Graph()
    for course in courses:
        g2022f.add_node("c" + course["subNum"], attr=course_to_data_dict(course))
        g2023s.add_node("c" + course["subNum"], attr=course_to_data_dict(course))

    for program in programs:
        g2022f.add_node(f"p{program['poid']}", attr=program_to_data_dict(program))
        g2023s.add_node(f"p{program['poid']}", attr=program_to_data_dict(program))
        for course_id in program["courses"]:
            g2022f.add_edge(f"p{section['poid']}", "c" + course_map[course_id])
            g2023s.add_edge(f"p{section['poid']}", "c" + course_map[course_id])

    for section in term2022f:
        g2022f.add_node(f"s{section['id']}", attr=section_to_data_dict(section))
        g2022f.add_edge(f"s{section['id']}", "c" + section_course_to_course(section["subjectCourse"]))
    for section in term2023s:
        g2023s.add_node(f"s{section['id']}", attr=section_to_data_dict(section))
        g2023s.add_edge(f"s{section['id']}", "c" + section_course_to_course(section["subjectCourse"]))

    return g2022f, g2023s

def distinct_communities(count_null=False, departments=False, program_type=False):
    f = open("programsData/programs_all.json")
    programs = json.load(f)
    f.close()
    
    communities = set()
    for program in programs:
        if program_type:
            if count_null or program["program_type"] is not None:
                communities.add(program["program_type"])
        elif departments:
            if count_null or program["department"] is not None:
                communities.add(program["department"])
        else:
            if count_null or program["college"] is not None:
                communities.add(program["college"])
    return list(communities)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or sys.argv[1] == "create":
        global g2022f
        global g2023s
        g2022f, g2023s = create_graphs()
    elif sys.argv[1] == "communities":
        global communities
        communities = distinct_communities()


# 'Community-Engaged Scholars Program'
# 'Caine College of the Arts Department of Art and Design'
# 'Objectives'
# 'S.J. and Jessie E. Quiney College of Natural Resources'
# 'Utah State University Advising'
# 'Please contact a specific college advisor from the list below for more information regarding how to apply for this major.'
# 'College of Science, Department of Physics'
# 'Utah State University-Eastern'

# courses[0]   = {'courseID': '285409', 'subNum': 'ACCT 2010', 'desc': 'Financial Accounting Principles'}
# term2022f[0] = {'id': 643201, 'term': '202240', 'termDesc': 'Fall 2022', 'courseReferenceNumber': '40025', 'sequenceNumber': '001', 'courseTitle': 'Financial Accounting Principles', 'maximumEnrollment': 79, 'enrollment': 47, 'seatsAvailable': 32, 'waitCapacity': 100, 'waitCount': 0, 'waitAvailable': 100, 'creditHourHigh': None, 'creditHourLow': 3, 'subjectCourse': 'ACCT2010', 'faculty': [{'displayName': 'Paul Campbell'}], 'instructionalMethodDescription': 'Face-to-Face'}
# term2022f[0] = {'term': '202240', 'termDesc': 'Fall 2022', }
# term2023s[0] = {'id': 659824, 'term': '202320', 'termDesc': 'Spring 2023', 'courseReferenceNumber': '10001', 'sequenceNumber': '001', 'courseTitle': 'Financial Accounting Principles', 'maximumEnrollment': 79, 'enrollment': 79, 'seatsAvailable': 0, 'waitCapacity': 100, 'waitCount': 13, 'waitAvailable': 87, 'creditHourHigh': None, 'creditHourLow': 3, 'subjectCourse': 'ACCT2010', 'faculty': [{'displayName': 'Lacee Wilkey'}], 'instructionalMethodDescription': 'Face-to-Face'}
