import requests
import re
import json
import os
import urllib
from dacite import from_dict
from DTO.course import CourseResDTO, CourseDTO
from DTO.material import MaterialDTO
from bs4 import BeautifulSoup
from dataclasses import asdict

ROOT = os.getcwd()

class MCVParser:
	def __init__(self, username: str, password: str):
		self.username = username
		self.password = password

		self.url = "https://www.mycourseville.com"
		self.session = requests.Session()
		self.token = ""
		self.cookies: dict[str, str] = {"has_js": "1"}

	def get_client(self) -> None:
		"""
		Extract and add necessary session cookies as a client
		cookies: laravel_session, XSRF-TOKEN, SESSeb912a58562fbbdf6ad5e9a19524d1c0
		"""
		r = self.session.get(self.url)
		self.cookies.update(r.cookies.get_dict())

		r = self.session.get(self.url + "/api/oauth/authorize?response_type=code&client_id=mycourseville.com&redirect_uri=https://www.mycourseville.com&login_page=itchula")
		self.cookies.update(r.cookies.get_dict())

	def get_token(self) -> None:
		r = self.session.get(
			self.url + "/api/chulalogin",
			cookies=self.cookies
		)
		res = re.search('<input type="hidden" name="_token" value="([A-Za-z0-9]+)">', r.text)

		if res:
			self.token = res.group(1)

	def login(self) -> bool:
		self.get_client()
		self.get_token()

		r = self.session.post(
			self.url + "/api/chulalogin",
			data={
				"username": self.username,
				"password": self.password,
				"_token": self.token
			},
			cookies=self.cookies
		)

		return "Log out" in r.text
	
	def get_all_yearsem(self) -> list[str]:
		r = self.session.get(
			self.url + "/?type=course&role=all",
			cookies=self.cookies
		)

		soup = BeautifulSoup(r.text, "html.parser")
		select = soup.find("select", {"id": "all-yearsem-select"})
		all_yearsem = [option["value"] for option in select.find_all("option")] # type: ignore

		return all_yearsem
	
	def get_courses(self) -> dict[str, list[CourseDTO]]:
		all_yearsem = self.get_all_yearsem()
		courses: dict[str, list[CourseDTO]] = {}

		for yearsem in all_yearsem:
			r = self.session.post(
				self.url + "/?q=courseville/ajax/cvhomepanel_get_filter",
				data={
					"yearsem": yearsem,
					"role": "all",
					"type": "course"
				},
				cookies=self.cookies
			)

			payload = json.loads(r.text)
			res = from_dict(CourseResDTO, payload)
			courses[yearsem] = res.data

		return courses
	
	def get_material(self, course_id: str) -> list[MaterialDTO]:
		r = self.session.get(
			self.url + "/?q=courseville/course/" + course_id,
			cookies=self.cookies
		)
		materials: list[MaterialDTO] = []

		soup = BeautifulSoup(r.text, "html.parser")
		materials_div = soup.find("div", {"class": "cvui-color-set-1-wrapper"})

		files_tr = materials_div.find_all("tr") # type: ignore
		
		# TODO: implement dfs from root for better perfomance ?
		for tr in files_tr:
			title = tr.find("td", {"data-col": "title"}).find("a").get_text().strip()
			link = tr.find("td", {"data-col": "action"}).find("a").get("href")
			
			path_lst = []
			# traverse back from leaf (file) to root
			for p in tr.parents:
				tagname = p.name
				classname = " ".join(p.get("class", []))

				if tagname != "div":
					continue

				# hit root
				if classname == "cvui-color-set-1-wrapper":
					break

				# hit parent folder
				if classname == "cv-course-home-folder-container cvui-colored-bg cvui-striped":
					folder_title = p.find("div", {"data-part": "title"}).get_text().strip()
					folder_name = re.sub(r'[^a-zA-Z0-9_-]', '', folder_title.replace(" ", "-")).lower()

					path_lst.append(folder_name)

			path = "/" + "/".join(reversed(path_lst))

			materials.append(MaterialDTO(path, title, link))

		return materials
	
	# TODO: refactor
	def dump_materials(self) -> None:
		courses = self.get_courses()
		
		for yearsem in courses:
			print(f"Year/semester: {yearsem}")

			for course in courses[yearsem]:
				print(f"   - {course.title}")

				materials = self.get_material(course.cv_cid)
				clear_set: set[str] = set()


				for material in materials:
					o = urllib.parse.urlparse(material.link)
					filename = o.path.rstrip("/").split("/")[-1]
					ext = filename.split(".")[-1] if "." in filename else ""

					folder_path = f"{ROOT}/Courses/{yearsem.replace("/", "-")}/{course.course_no.replace('.', '-')}{material.path}"

					os.makedirs(folder_path, exist_ok=True)

					try:
						if ext == "":
							path = os.path.join(folder_path, "link.txt")

							if path not in clear_set:
								open(path, "w").close()
								clear_set.add(path)

							with open(path, "a") as f:
								f.write(f"{material.title} - {material.link}\n")
						else:
							path = os.path.join(folder_path, filename)
							url = o._replace(path=urllib.parse.quote(o.path)).geturl()
							file = urllib.request.urlopen(url)

							with open(path, "wb") as f:
								f.write(file.read())
					except Exception as e:
						print(f"{material.title}: {e}")

				# Course materials
				folder_path = f"{ROOT}/Courses/{yearsem.replace("/", "-")}/{course.course_no.replace('.', '-')}/materials.json"
				with open(folder_path, "w") as f:
					materials_lst = [] # type: ignore
					for i in materials:
						d = asdict(i)
						o = urllib.parse.urlparse(i.link)
						filename = o.path.rstrip("/").split("/")[-1]
						d["filename"] = filename
						materials_lst.append(d)
					
					f.write(json.dumps(materials_lst, indent=4, ensure_ascii=False))

				# Course metadata
				folder_path = f"{ROOT}/Courses/{yearsem.replace("/", "-")}/{course.course_no.replace('.', '-')}/metadata.json"
				with open(folder_path, "w") as f:
					f.write(json.dumps(asdict(course), indent=4, ensure_ascii=False))
			
			print()