from mcv import MCVParser

if __name__ == "__main__":
	student_id = input("Student ID (10 digits): ")
	password = input("Password: ")
	mcvp = MCVParser(student_id, password)

	if mcvp.login():
		mcvp.dump_materials()
	else:
		print("Incorrect username or password")