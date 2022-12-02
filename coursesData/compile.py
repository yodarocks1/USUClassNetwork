import os
import json
dir = 'coursesData/CourseIDsNumsDescs'

crs_in_pgs = []

crs_in_one = []
for file in os.scandir(dir):
    f = open(file)
    data = json.load(f)

    crs_in_pgs.append(data)
    crs_in_one += data

file1 = open('courses_in_pages.json', 'w')
file1.write(f'{crs_in_pgs}')
file1.close()
file2 = open('courses_in_one.json', 'w')
file2.write(f'{crs_in_one}')
file2.close()