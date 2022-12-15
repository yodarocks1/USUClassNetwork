import json
import networkx as nx
import re
import matplotlib
import csv
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

def load_csv(filepath, has_header=True):
    f = open(filepath)
    lines = list(csv.reader(f))
    f.close()
    if has_header:
        headers = list(map(lambda v: v.strip(), lines[0]))
        lines = lines[1:]

    data = []
    for line in lines:
        if has_header:
            datum = {}
            c = line
            for i in range(len(headers)):
                datum[headers[i]] = c[i].strip()
        else:
            datum = map(lambda v: v.strip(), line)
        data.append(datum)
    return data

def load_registrar_data():
    filepath = "registrar_data.csv"
    csv = load_csv(filepath)
    class lister:
        def __init__(self, headers):
            self.headers = headers
            self._dict = {}
            self._set = []
        def _read_datum(self, datum):
            r = []
            for header in self.headers:
                r.append(datum[header])
            return r
        def add_datum(self, datum, update_set=True):
            data = self._read_datum(datum)
            d = self._dict
            for i in range(len(self.headers) - 1):
                if data[i] not in d:
                    d[data[i]] = {}
                d = d[data[i]]
            if data[-1] not in d:
                d[data[-1]] = []
            d[data[-1]].append(datum)
            if update_set:
                self.update_set()
        def update_set(self):
            data = list(map(lambda x: [x], self._dict.keys()))
            for i in range(len(self.headers) - 1):
                new_data = []
                for datum in data:
                    for k in self.get(datum):
                        new_data.append([*datum, k])
                data = new_data
            self._set = data
            return self._set
        def get(self, getters):
            d = self._dict
            for getter in getters:
                d = d[getter]
            return d
        def set(self):
            return self._set
        def dict(self):
            return self._dict
        def __len__(self):
            return len(self._set)
    listers = {
        "degrees": lister(["STUDENT_LEVEL", "DEGREE_DESC", "DEGREE_LEVEL"]),
        "programs": lister(["PROGRAM_DESC"]),
        "colleges": lister(["COLLEGE_DESC"]),
        "departments": lister(["COLLEGE_DESC", "DEPARTMENT_DESC"]),
        "majors": lister(["COLLEGE_DESC", "DEPARTMENT_DESC", "MAJOR_DESC"]),
        "concentrations": lister(["COLLEGE_DESC", "DEPARTMENT_DESC", "MAJOR_DESC", "CONCENTRATION_DESC"]),
        "courses": lister(["SUBJECT", "COURSE_NUMBER"])
    }
    for datum in csv:
        for k in listers:
            listers[k].add_datum(datum, update_set=False)
    for k in listers:
        listers[k].update_set()
    return listers

# STUDENT_LEVEL,DEGREE,DEGREE_DESC,DEGREE_LEVEL,DEGREE_LEVEL_NUMERIC_VALUE,
# PROGRAM,PROGRAM_DESC,PROGRAM_CATALOG_TERM,
# COLLEGE_CODE,COLLEGE_DESC,
# DEPARTMENT_CODE,DEPARTMENT_DESC,
# MAJOR_CODE,MAJOR_DESC,MAJOR_CIP_CODE,
# CONCENTRATION_CODE,CONCENTRATION_DESC,CONCENTRATION_CIP_CODE,
# STUDENT_COUNT_IN_PROGRAM_FALL_2022,
# SUBJECT,COURSE_NUMBER,COURSE_TITLE,STUDENT_COUNT_TAKEN_COURSE


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

def registrar_to_data_dict(rows):
    return rows
    #if len(rows) == 0:
    #    return {}
    #result = {}
    #for key in rows[0]:
    #    if key in ["SUBJECT", "COURSE_NUMBER"]:
    #        result["SUB_NUM"] = set()
    #    else:
    #        result[key] = set()
    #for item in rows:
    #    for key in item:
    #        if key == "SUBJECT":
    #            result["SUB_NUM"].add(item["SUBJECT"] + " " + item["COURSE_NUMBER"])
    #        elif key == "COURSE_NUMBER":
    #            continue
    #        else:
    #            result[key].add(item[k])
    #return result

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

    colleges = dict()
    departments = dict()
    for program in programs:
        if program["college"] not in colleges:
            colleges[str(program["college"])] = []
        colleges[program["college"]].append(str(program["department"]))
        if program["department"] not in departments:
            departments[str(program["department"])] = []
        departments[str(program["department"])].append(program["poid"])

    course_map = course_id_map(courses)
    registrar_data = load_registrar_data()
    
    g_registrar = nx.Graph()
    for program in registrar_data["programs"].set():
        g_registrar.add_node(f"p{program[0]}", attr=registrar_to_data_dict(registrar_data["programs"].dict()[program[0]]), bipartite=0)
    for course in registrar_data["courses"].set():
        course_data = registrar_to_data_dict(registrar_data["courses"].dict()[course[0]][course[1]])
        g_registrar.add_node(f"c{course[0]} {course[1]}", attr=course_data, bipartite=1)
        for row in course_data:
            w = int(row["STUDENT_COUNT_TAKEN_COURSE"]) / int(row["STUDENT_COUNT_IN_PROGRAM_FALL_2022"])
            g_registrar.add_edge(f"c{course[0]} {course[1]}", f"p{row['PROGRAM']}", weight=w)

    # BIPARTITE:
    # 0:g - Colleges
    # 1:d - Departments
    # 2:p - Programs
    # 3:c - Courses
    # 4:s - Sections

    g2022f = nx.Graph()
    g2023s = nx.Graph()
    for course in courses:
        g2022f.add_node("c" + course["subNum"], attr=course_to_data_dict(course), bipartite=3)
        g2023s.add_node("c" + course["subNum"], attr=course_to_data_dict(course), bipartite=3)

    for program in programs:
        g2022f.add_node(f"p{program['poid']}", attr=program_to_data_dict(program), bipartite=2)
        g2023s.add_node(f"p{program['poid']}", attr=program_to_data_dict(program), bipartite=2)
        for course_id in program["courses"]:
            g2022f.add_edge(f"p{program['poid']}", "c" + course_map[course_id])
            g2023s.add_edge(f"p{program['poid']}", "c" + course_map[course_id])
    
    for department in departments:
        g2022f.add_node("d" + department, bipartite=1)
        g2023s.add_node("d" + department, bipartite=1)
        for program in departments[department]:
            g2022f.add_edge("d" + department, "p" + program)
            g2023s.add_edge("d" + department, "p" + program)
    for college in colleges:
        g2022f.add_node("g" + college, bipartite=0)
        g2023s.add_node("g" + college, bipartite=0)
        for department in colleges[college]:
            g2022f.add_edge("g" + college, "d" + department)
            g2023s.add_edge("g" + college, "d" + department)

    for section in term2022f:
        g2022f.add_node(f"s{section['id']}", attr=section_to_data_dict(section), bipartite=4)
        g2022f.add_edge(f"s{section['id']}", "c" + section_course_to_course(section["subjectCourse"]))
    for section in term2023s:
        g2023s.add_node(f"s{section['id']}", attr=section_to_data_dict(section), bipartite=4)
        g2023s.add_edge(f"s{section['id']}", "c" + section_course_to_course(section["subjectCourse"]))

    return g2022f, g2023s, g_registrar

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
        global g_registrar
        g2022f, g2023s, g_registrar = create_graphs()
    elif sys.argv[1] == "communities":
        global communities
        communities = distinct_communities()
    elif sys.argv[1] == "registrar":
        global data
        data = load_registrar_data()


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
