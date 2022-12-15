import requests
from bs4 import BeautifulSoup
import json
import re

class Program:
    def __init__(self, poid, desc, college, department, required_courses):
        self.poid = poid
        self.desc = desc
        self.college = college
        self.department = department
        self.required_courses = required_courses
        if self.college is not None:
            self.college = self.college.strip().replace("\xa0", " ").replace("&", "and")
        if self.department is not None:
            self.department = self.department.strip().replace("\xa0", " ").replace("&", "and")
        if self.college is not None and self.college.startswith("Department"):
            a = self.college
            self.college = self.department
            self.department = a
    def __str__(self):
        return f"{self.desc} ({self.college} \\ {self.department}): {len(self.required_courses)} Required"
    def dict(self):
        return {
            "poid": self.poid,
            "desc": self.desc,
            "college": self.college,
            "department": self.department,
            "courses": self.required_courses
        }

def fetch_all():
    url = "https://catalog.usu.edu/content.php?catoid=35&navoid=26809"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    name_map = {"h3": 0, "h4": 1, "strong": 2}

    def format_from(data, next_data):
        d = data
        for i in range(2):
            if next_data[i] not in d:
                d[next_data[i]] = {}
            d = d[next_data[i]]
        if next_data[2] not in d:
            d[next_data[2]] = []

    data = {}
    next_data = [None] * 3
    v = soup.find(id="ent3512").find_next()

    while v is not None:
        if v.name in name_map:
            next_data[name_map[v.name]] = v.text.strip()
            for i in range(name_map[v.name] + 1, 3):
                next_data[i] = None
        elif v.name == "a" and "href" in v.attrs and v.attrs["href"].startswith("preview_program.php?"):
            format_from(data, next_data)
            data[next_data[0]][next_data[1]][next_data[2]].append({
                    "href": "https://catalog.usu.edu/" + v.attrs["href"],
                    "desc": v.text.strip()
            })
        v = v.find_next()
    return data
                    

def get_program(url):
    poid = url[url.index("poid=") + 5:url.index("&returnto=")]
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')
    anchors1 = soup.select("a[href^=\"showCourse\"]")
    anchors2 = soup.select("a[href^=\"acalogPopup\"]")
    anchors3 = soup.select("a[href^=\"showCatalogData\"]")
    courses = []
    for anchor in anchors1:
        courses.append(anchor.attrs["onclick"].split(",")[1].strip().replace("'", ""))
    for anchor in anchors2:
        courses.append(anchor.attrs["onclick"].split("'")[1].strip().replace("&print", "").replace("preview_course.php?catoid=35&coid=", ""))
    for anchor in anchors3:
        courses.append(anchor.attrs["onclick"].split(",")[2].strip().replace("'", ""))
    desc = soup.select_one("#acalog-content").text
    header = soup.select_one(".program_description")
    header1 = header.find_next()
    header2 = header1.find_next()
    if header1.name == "h1" or header1.name == "h2":
        college = header1.text.strip().replace("\n\r\n", "; ")
        if ";" in college:
            department = re.split("[;]", college)[1].strip()
            college = re.split("[;]", college)[0].strip()
        elif header2.name == "h1" or header1.name == "h2":
            department = header2.text.strip()
            if len(department) == 0:
                department = None
        else:
            department = None
        if len(college) == 0:
            college = None
    else:
        college = None
        department = None
    return Program(poid, desc, college, department, courses).dict()

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "getall":
        data = fetch_all()
        f = open(sys.argv[2], 'x')
        json.dump(data, f)
        f.close()
    elif sys.argv[1] == "all":
        data = fetch_all()
        programs = []
        for college in data:
            for department in data[college]:
                for program_type in data[college][department]:
                    for program in data[college][department][program_type]:
                        p = get_program(program["href"])
                        p["college"] = college
                        p["department"] = department
                        p["program_type"] = program_type
                        programs.append(p)
        f = open(sys.argv[2], "x")
        json.dump(programs, f)
        f.close()
    else:
        f = open(sys.argv[1])
        j = json.load(f)
        f.close()
        programs = []
        i = 0
        l = len(j)
        print(l)
        for prog in j:
            programs.append(get_program(prog["href"]))
            if sys.argv[-1] == "1":
                break
            i += 1
            if i % 10 != 0:
                print(".", end="")
            else:
                print(f": {i}/{l}")
        f = open(sys.argv[2], "x")
        json.dump(programs, f)
        f.close()

