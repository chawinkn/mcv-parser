import requests
import re
import json
import os
import urllib
import datetime
import time
import questionary
from dacite import from_dict
from DTO.course import CourseResDTO, CourseDTO
from DTO.material import MaterialDTO
from bs4 import BeautifulSoup
from dataclasses import asdict
from rich.console import Console

ROOT = os.getcwd()
console = Console()

class MCVParser:
    def __init__(self, username: str, password: str, delay: float = 10.0):
        self.username = username
        self.password = password

        self.url = "https://www.mycourseville.com"
        self.session = requests.Session()
        self.token = ""
        self.cookies: dict[str, str] = {"has_js": "1"}
        self.last_request_time = 0.0
        self.crawl_delay = max(0.0, delay)

    def _throttle(self) -> None:
        """Ensures at least crawl_delay seconds have passed since the last request."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.crawl_delay:
            wait_time = self.crawl_delay - elapsed
            time.sleep(wait_time)
        self.last_request_time = time.time()

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
        if not select:
            return []
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

            try:
                payload = json.loads(r.text)
                res = from_dict(CourseResDTO, payload)
                courses[yearsem] = res.data
            except json.JSONDecodeError:
                continue

        return courses

    def get_material(self, course_id: str) -> list[MaterialDTO]:
        r = self.session.get(
            self.url + "/?q=courseville/course/" + course_id,
            cookies=self.cookies
        )
        materials: list[MaterialDTO] = []

        soup = BeautifulSoup(r.text, "html.parser")
        materials_div = soup.find("div", {"class": "cvui-color-set-1-wrapper"})

        if not materials_div:
            return []

        files_tr = materials_div.find_all("tr") # type: ignore

        for tr in files_tr:
            title_td = tr.find("td", {"data-col": "title"})
            action_td = tr.find("td", {"data-col": "action"})

            if not title_td or not action_td:
                continue

            title_a = title_td.find("a")
            link_a = action_td.find("a")

            if not title_a or not link_a:
                continue

            title = title_a.get_text().strip()
            link = link_a.get("href")

            path_lst = []
            for p in tr.parents:
                tagname = p.name
                classname = " ".join(p.get("class", []))

                if tagname != "div":
                    continue

                if classname == "cvui-color-set-1-wrapper":
                    break

                if classname == "cv-course-home-folder-container cvui-colored-bg cvui-striped":
                    folder_title_div = p.find("div", {"data-part": "title"})
                    if not folder_title_div:
                        continue
                    folder_title = folder_title_div.get_text().strip()
                    folder_name = re.sub(r'[^a-zA-Z0-9_-]', '', folder_title.replace(" ", "-")).lower()

                    path_lst.append(folder_name)

            path = "/" + "/".join(reversed(path_lst))

            materials.append(MaterialDTO(path, title, link))

        return materials

    def dump_materials(self) -> None:
        with console.status("[bold yellow]🔍 Fetching available semesters and courses...[/bold yellow]"):
            all_yearsem = self.get_all_yearsem()
            if not all_yearsem:
                console.print("[bold red]⚠️  No semesters found![/bold red]")
                return

            # Filter yearsem that actually have courses
            valid_courses_map: dict[str, list[CourseDTO]] = {}
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
                try:
                    payload = json.loads(r.text)
                    res = from_dict(CourseResDTO, payload)
                    if res.data: # Only add if there are courses
                        valid_courses_map[yearsem] = res.data
                except json.JSONDecodeError:
                    continue

        if not valid_courses_map:
            console.print("[bold red]⚠️  No courses found in any semester![/bold red]")
            return

        available_semesters = list(valid_courses_map.keys())
        selected_yearsem = questionary.checkbox(
            "Select semesters to download",
            choices=available_semesters,
            instruction="(Space to select, a to select all, Enter to confirm)"
        ).ask()

        if not selected_yearsem:
            console.print("[bold yellow]ℹ️  No semesters selected. Exiting.[/bold yellow]")
            return

        scrape_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Filter the map based on user selection
        courses = {ys: valid_courses_map[ys] for ys in selected_yearsem}

        console.print(f"\n[bold magenta]🚀 Starting material download (Session: {scrape_time})...[/bold magenta]\n")

        for yearsem in courses:
            console.print(f"[bold cyan]📅 {yearsem}[/bold cyan]")

            for course in courses[yearsem]:
                console.print(f"  [bold blue]📘 {course.course_no} {course.title}[/bold blue]")

                with console.status(f"    [italic white]Checking for materials...[/italic white]"):
                    materials = self.get_material(course.cv_cid)

                if not materials:
                    console.print("    [yellow]⚠️  No materials found for this course.[/yellow]")
                    continue

                course_folder = f"{ROOT}/Courses_{scrape_time}/{yearsem.replace('/', '-')}/{course.course_no.replace('.', '-')}"
                os.makedirs(course_folder, exist_ok=True)

                clear_set: set[str] = set()

                for material in materials:
                    o = urllib.parse.urlparse(material.link)
                    filename = o.path.rstrip("/").split("/")[-1]
                    ext = filename.split(".")[-1] if "." in filename else ""
                    folder_path = f"{course_folder}{material.path}"
                    os.makedirs(folder_path, exist_ok=True)

                    try:
                        if ext == "":
                            path = os.path.join(folder_path, "link.txt")
                            if path not in clear_set:
                                open(path, "w").close()
                                clear_set.add(path)
                            with open(path, "a") as f:
                                f.write(f"{material.title} - {material.link}\n")
                            console.print(f"    [green]🔗 Saved link:[/green] [white]{material.title}[/white]")
                        else:
                            path = os.path.join(folder_path, filename)
                            # Using status here just for the individual file download so it's snappy
                            with console.status(f"    [italic white]Downloading {filename}...[/italic white]"):
                                # Only throttle on file downloads
                                self._throttle()
                                r = self.session.get(material.link, cookies=self.cookies, stream=True)
                                r.raise_for_status()
                                with open(path, "wb") as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            console.print(f"    [green]✅ Downloaded:[/green] [white]{filename}[/white]")
                    except Exception as e:
                        console.print(f"    [bold red]❌ Failed: {material.title} ({e})[/bold red]")

                # save metadata files
                folder_path_mat = os.path.join(course_folder, "materials.json")
                with open(folder_path_mat, "w") as f:
                    materials_lst = []
                    for i in materials:
                        d = asdict(i)
                        o = urllib.parse.urlparse(i.link)
                        d["filename"] = o.path.rstrip("/").split("/")[-1]
                        materials_lst.append(d)
                    f.write(json.dumps(materials_lst, indent=4, ensure_ascii=False))

                folder_path_meta = os.path.join(course_folder, "metadata.json")
                with open(folder_path_meta, "w") as f:
                    f.write(json.dumps(asdict(course), indent=4, ensure_ascii=False))

            console.print("")

        console.print("[bold green]✨ All tasks completed successfully![/bold green]")
