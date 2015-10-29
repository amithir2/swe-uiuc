import subprocess
import os
from collections import defaultdict
MAJOR = 'student_major_name'
ADDRESS = 'address'
LEVEL = 'student_level_description'
KEYS = [ MAJOR, ADDRESS, LEVEL]

def filters(results):
	final_results = []
	for result in results:
		if MAJOR not in result: 
			continue
		if LEVEL not in result:
			continue
		if ADDRESS not in result:
			result[ADDRESS] = None
		final_results.append(result)
	if len(final_results) < 1:
		d = {}
		for key in KEYS:
			d[key] = None
		return d
	else:
		return final_results[-1]

def nph_query(firstname, lastname):
	command = ['nph', firstname, lastname]
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = process.communicate()	
	if 'no matches to query' in out:
		command = ['nph', lastname]
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = process.communicate()

	out = out.split('\n')
	out = [each.lower() for each in out if ':'in each]
	return out

def get_nph(names):
	students = []
	for (firstname, lastname) in names:
		out = nph_query(firstname, lastname)

		curr_index = -1
		results = []
		prev_key = ''
		for line in out:
			if 'entry' in line:
				curr_index += 1
				results.append({})
				continue
			if curr_index < 0:
				continue
			if ':' in line:
				text = line.split(':')
				if len(text) < 2: continue
				key = text[0].strip()
				value = text[1].strip()
				if len(key) == 0:
					key = prev_key
					results[curr_index][key] += (' ' + value)
				else:
					results[curr_index][key] = value
				prev_key = key

		results = filters(results)

		students.append(results)

	return students

def parseMembers(filename):
	with open(filename, 'rb') as f:
		lines = f.readlines()

	names = []
	for line in lines[1:]:
		data = line.split(',')
		firstname = data[0].lower()
		lastname = data[1].lower()
		names.append([firstname, lastname])
	return names

def extract_major(students):
	majors = defaultdict(int)
	for student in students:
		major = student[MAJOR]
		majors[major] += 1
	return majors

def extract_student_level(students):
	student_levels = defaultdict(int)
	for student in students:
		student_level = student[LEVEL]
		student_levels[student_level] += 1
	return student_levels

def extract_address(students):
	addresses = []
	for student in students:
		addresses.append(student[ADDRESS])
	return addresses

def get_majors(students):
	majors = extract_major(students)
	total = sum(majors.values())
	for major in majors:
		print major,'\t', float(majors[major])/total

def get_addresses(students):
	addresses = extract_address(students)
	with open('addresses.txt', 'wb') as f:
		for address in addresses:
			f.write(str(address))
			f.write('\n')

def get_student_level(students):
	student_levels = extract_student_level(students)
	total = sum(student_levels.values())
	for student_level in student_levels:
		print student_level,'\t', float(student_levels[student_level])/total


def get_statistics(filename):
	names = parseMembers(filename)
	students = get_nph(names)
	# get_majors(students)
	# get_addresses(students)
	get_student_level(students)
	

if __name__ == '__main__':
	get_statistics('nat-mem.txt')
