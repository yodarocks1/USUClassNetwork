import requests
import re

class Catalog:
    def __init__(self, idx):
        self.idx = idx
    def get_all_programs(self):
        result = requests.get(f"https://catalog.usu.edu/content.php?catoid={self.idx}&navoid=26598")
        programs = result.text
        programs = programs.split('<ul class="program-list">')[1].split("</ul>")[0]
        programs = re.sub(r"&returnto=[0-9]+", "", programs)
        programs = programs.split('<li style="list-style-type: none">&#8226;&#160;\n')[1:]
        prog = []
        for program in programs:
            poid_start = program.index("poid=") + 5
            poid_end = program.index("\">", poid_start)
            poid = program[poid_start:poid_end]
            pgm_end = program.index("</a>")
            pgm = program[poid_end + 2:pgm_end]
            prog.append((pgm, int(poid)))
        return prog
    def get_program_details(self, program_id):
        result = requests.get(f"https://catalog.usu.edu/preview_program.php?catoid={self.idx}&poid={program_id}")
        result = result.text
        courses = []
        i = result.find("acalog-course")
        while i != -1:
            onclick_start = result.lower().index("onclick=", i) + 8
            onclick_end = result.index("\"", onclick_start + 1)
            onclick = result[onclick_start:onclick_end]
            coid_start = onclick.index(", '") + 3
            coid_end = onclick.index("'", coid_start)
            coid = onclick[coid_start:coid_end]
            name_start = result.index(">", onclick_end) + 1
            name_end = result.index("</a>", name_start)
            name = result[name_start:name_end]
            courses.append((name, coid))
            i = result.find("acalog-course", name_end + 4)
        return courses

class Term:
    def __init__(self, input_dict):
        self.code = input_dict["code"]
        self.desc = input_dict["description"].replace(" (View Only)", "")
    def __str__(self):
        return self.desc
    def __repr__(self):
        return "Term{" + self.desc + " | " + self.code + "}"

class Course:
    def __init__(self, raw):
        self.raw = raw
        self.dict = dict(raw)
    def __str__(self):
        return f"{self.dict['subjectCourse']}: {self.dict['courseTitle']} ({self.dict['faculty'][0]['displayName']})"
    def __repr__(self):
        return "Course{" + self.dict["subjectCourse"] + " | " + str(self.dict["id"]) + "}"
    def __getitem__(self, i):
        return self.dict[i]

class Session:
    def __init__(self, sessionId, cookies):
        self.sessionId = sessionId
        self.cookies = cookies

class IdeaAssessments:
    def __init__(self, course, session=None):
        if session is not None:
            headers = {"cookie": session.cookies}
        else:
            headers = {}
        global search_result
        search_result = requests.get(f"https://www.usu.edu/aaa/evaluations_all.cfm?src={course['subject']}+{course['courseNumber']}",
                headers=headers,
            )
        self.search_content = str(search_result.content).replace("\\n", "\n").replace("\\r", "")
        start_idx = self.search_content.find("PDF</td>\n</tr>") + 14
        end_idx = self.search_content.find("</table></center>")
        self.rows = self.search_content[start_idx:end_idx].split("<tr>\n\n\n<tr>")

    def get_row_data(self, i):
        r = self.rows[i]
        href_start = r.find("href=") + 5
        href_end = r.find(" ", href_start)
        href = r[href_start:href_end]
        r = r.replace(href, "")
        data = {}
        order = ["courseName", "instructor", "term, year", "score", "responses", "enrolled", "rate"]
        for line in r.split("\n"):
            if "href= >" in line:
                x = line.index("href= >") + 7
                y = line.index("</a>")
                data[order.pop(0)] = line[x:y]
            elif "<font color=silver>" in line and len(order) > 0:
                x = line.index("<font color=silver>") + 19
                y = line.index("</font>")
                data[order.pop(0)] = line[x:y]

        term_code = data["term, year"].split(", ")
        if term_code[0] == "Spring":
            term_code = term_code[1] + "20"
        elif term_code[0] == "Summer":
            term_code = term_code[1] + "30"
        elif term_code[0] == "Fall":
            term_code = term_code[1] + "40"
        instructor = data["instructor"].split(", ")
        instructor = instructor[1] + " " + instructor[0]

        return {
            "href": href,
            "subjectCourse": re.sub(r"\(.*?\)", "", data["courseName"].replace(" ", "")),
            "term": term_code,
            "instructor": instructor,
            "score": {
                "responses": data["responses"],
                "enrolled": data["enrolled"],
                "value": data["score"],
            }
        }

    def find_row_for_course(self, course):
        for i in range(len(self.rows)):
            row_data = self.get_row_data(i)
            if course["faculty"][0]["displayName"] == row_data["instructor"] \
                and course["term"] == row_data["term"] \
                and course["subjectCourse"] == row_data["subjectCourse"]:
                    return (i, row_data)
        return (-1, None)
                

test_course = {'id': 658779, 'term': '202230', 'termDesc': 'Summer 2022', 'courseReferenceNumber': '32526', 'partOfTerm': 'D1', 'courseNumber': '1400', 'subject': 'CS', 'subjectDescription': 'Computer Science', 'sequenceNumber': 'AB1', 'campusDescription': 'Blanding Campus', 'scheduleTypeDescription': 'Interactive Broadcast', 'courseTitle': 'Introduction to Computer Science--CS 1', 'creditHours': 4, 'maximumEnrollment': 40, 'enrollment': 1, 'seatsAvailable': 39, 'waitCapacity': 100, 'waitCount': 0, 'waitAvailable': 100, 'crossList': '0765', 'crossListCapacity': 80, 'crossListCount': 21, 'crossListAvailable': 59, 'creditHourHigh': 4, 'creditHourLow': 0, 'creditHourIndicator': 'OR', 'openSection': True, 'linkIdentifier': None, 'isSectionLinked': False, 'subjectCourse': 'CS1400', 'faculty': [{'bannerId': '3767', 'category': None, 'class': 'net.hedtech.banner.student.faculty.FacultyResultDecorator', 'courseReferenceNumber': '32526', 'displayName': 'Chad Mano', 'emailAddress': 'chad.mano@usu.edu', 'primaryIndicator': True, 'term': '202230'}]}


def main():
    print("GET:\n\t1. Term(s)\n\t2. Course(s)")
    mode = input("  Desired option: ")
    if mode not in ["1","2"]:
        raise ValueError("Invalid option: " + mode)
    if mode == "1":
        print("\nGET TERMS:\n\t1. All\n\t2. N most recent")
        much = input("  Desired option: ")
        if much not in ["1","2"]:
            raise ValueError("Invalid option: " + much)
        if much == "1":
            terms = getAllTerms()
        else:
            n = int(input("\tAmount: "))
            terms = getTerms(1, n)
        print("\n===========================\nTerms:")
        for term in terms:
            print(f"  {term.desc:>11s} (code {term.code})")
        print("===========================")
    elif mode == "2":
        print("\nGET COURSES:")
        sessionId = input("  Session ID: ")
        cookies = input("  Cookies: ")
        s = Session(sessionId, cookies)
        print("\nGET COURSES:\n\t1. All (WARNING: Extremely time intensive)\n\t2. For given term")
        much = input("  Desired option: ")
        if much not in ["1","2"]:
            raise ValueError("Invalid option: " + much)
        if much == 1:
            do_write = input("\tWrite to files? [y/N]: ")
            if do_write.lower().strip() not in ["", "y","n"]:
                raise ValueError("Unknown option not in ['', 'y', 'n']: " + do_write)
            do_write = do_write.lower().strip() == "y"
            courses = getAllCourses(write=do_write, session=s)
        else:
            term = None
            offset = 1
            groupSize = 4
            terms = getTerms(offset, groupSize)
            while term is None:
                print("SELECT TERM:")
                if offset > 1:
                    print("\t0. See newer terms")
                for idx, term in enumerate(terms):
                    print(f"\t{idx + 1}. {term.desc}")
                if len(terms) == groupSize:
                    print(f"\t{groupSize + 1}. See previous terms")
                    print(f"\t{groupSize + 2}. See all terms")
                n = input("  Desired option: ")
                if offset > 1 and n == "0":
                    print("A")
                    offset -= 1
                    terms = getTerms(offset, groupSize)
                elif len(terms) == groupSize and int(n) - groupSize in [1, 2]:
                    print("B")
                    if int(n) == groupSize + 1:
                        print("C")
                        offset += 1
                        terms = getTerms(offset, groupSize)
                    elif int(n) == groupSize + 2:
                        print("D")
                        offset = 1
                        terms = getAllTerms()
                elif int(n) > 0 and int(n) <= len(terms):
                    print("E")
                    term = terms[int(n) - 1]
                else:
                    print("F")
                    raise ValueError("Invalid term option: " + n)
                print("G")
            courses = getAllTermCourses(term.code, session=s)
        print("\n===========================\nCourses:")
        for course in courses:
            instructor = "Unknown"
            if len(course["faculty"]) > 0:
                instructor = course["faculty"][0]["displayName"]
            print(f"{course['subjectCourse']} taught by {instructor}")
        print("===========================")

def getAllTerms(groupSize=10):
    terms = []
    c = 1
    while True:
        new_terms = getTerms(c, groupSize)
        terms.extend(new_terms)
        c += 1
        if len(new_terms) < groupSize:
            break
    return terms
def getTerms(offset, count):
    terms = requests.get("https://ss.banner.usu.edu/StudentRegistrationSsb/ssb/classSearch/getTerms",
            params={
                "offset": offset,
                "max": count,
            }
        )
    return list(map(Term, terms.json()))


def getAllCourses(session=None, groupSize=50, write=None):
    courses = {}
    terms = getAllTerms()
    for term in terms:
        courses[term] = getAllTermCourses(term.code, session=session, write=write)
    return courses
def getAllTermCourses(termCode, session=None, groupSize=50, write=None):
    courses = []
    c = 0
    while True:
        new_courses = getTermCourses(termCode, c, groupSize, session=session, write=write)
        courses.extend(new_courses)
        c += groupSize
        if len(new_courses) < groupSize:
            break
    return courses
def getTermCourses(termCode, offset, count, session=None, write=None):
    if session is not None:
        uniqueSessionId = {"uniqueSessionId": session.sessionId}
        headers = {"Cookie": session.cookies}
    else:
        uniqueSessionId = {}
        headers = {}
    global data
    data = requests.get("https://ss.banner.usu.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?startDatepicker=&endDatepicker=",
            params={
                "txt_term": termCode,
                "sortColumn": "subjectDescription",
                "sortDirection": "asc",
                "pageOffset": str(offset),
                "pageMaxSize": str(count),
                **uniqueSessionId,
            },
            headers={
                **headers,
                "Accept": "application/json, text/javascript, */*; q=0.01",
            },
        )
    if write is True:
        write = termCode + "x" + str(offset) + ".json"
    if write is not None:
        f = open(write, 'x')
        f.write(str(data.json()["data"]))
        f.close()
    if data.json()["data"] is None:
        return []
    return list(map(Course, data.json()["data"]))


def getData(pageOffset, pageSize):
    return requests.get(url,
            params={
                "uniqueSessionId": sessionId,
                "startDatepicker": "",
                "endDatepicker": "",
                "sortColumn": "subjectDescription",
                "sortDirection": "asc",
                "pageOffset": pageOffset,
                "pageMaxSize": pageSize,
            },
            headers={
                **headers,
                "Cookie": cookie,
            }
        )

