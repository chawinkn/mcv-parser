from dataclasses import dataclass
from typing import List

@dataclass
class CourseDataDTO:
	course_no: str
	year: str
	semester: str
	section: str
	role: str
	cv_cid: str

@dataclass
class CourseDTO:
	cv_cid: str
	course_no: str
	title: str
	year: str
	semester: str
	thumb_location: str
	default_material_thumb: str
	org_id: str
	school_id: str
	dept_id: str
	nid: str
	course_type: str
	role: str
	course: CourseDataDTO
	
@dataclass
class CourseResDTO:
	status: int
	data: List[CourseDTO]