import subprocess
import os
from collections import defaultdict

def extract_major(students):
	majors = defaultdict(int)
	for student in students:
		major = student['student_major_name']
		majors[major] += 1
	return majors

def filters(results):
	final_results = []
	for result in results:
		if 'student_major_name' not in result: 
			continue
		if 'student_level_description' not in result:
			continue
	#	if 'undergrad' not in result['student_level_description']:
	#		continue
		final_results.append(result)
	if len(final_results) < 1:
		return {'student_major_name': None}
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
				results[curr_index][key] = value

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

def get_statistics(filename):
	names = parseMembers(filename)
	students = get_nph(names)
	majors = extract_major(students)
	total = sum(majors.values())
	sums = 0
	for major in majors:
		sums += majors[major]
		print major,'\t', float(majors[major])/total
	print sums, total

if __name__ == '__main__':
	get_statistics('nat-mem.txt')
