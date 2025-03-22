from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field, validator


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseEduModel(BaseModel):
    id: Union[PyObjectId, str] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AnswerModel(BaseModel):
    text: Optional[str]
    url: Optional[str]
    original: Optional[bool]
    metadata: Optional[Dict]

    class Config:
        schema_extra = {
            "example": {
                "text": "True",
                "url": "url",
                "original": True,
                "metadata": {},
            }
        }


class Creator(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class GroupModel(BaseEduModel):
    name: Optional[str]
    description: Optional[str]
    group_type: Optional[str]
    image_url: Optional[str]
    visibility: Optional[str]
    members: Optional[Any] = 0
    created_by: str
    creator: Optional[Creator]
    tag_text: List[str] = []

    @validator("members")
    def members_length(cls, v):
        return len(v)


class AgeGroup(BaseModel):
    id: int
    name: str
    min_age: int
    max_age: int


class ContentModel(BaseEduModel):
    description: Optional[str]
    data: Optional[str]
    type: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "description": "Content description.",
                "data": "2021-07-06T13:47:43.207Z",
                "type": "text",
            }
        }


class MicroLessonModel(BaseEduModel):
    title: Optional[str]
    content: Optional[ContentModel]
    topics: Optional[List[str]]
    age_group: Optional[AgeGroup]
    tag_text: List[str] = []
    questions: Optional[List[PyObjectId]]

    class Config:
        schema_extra = {
            "example": {
                "title": "MicroLesson title.",
                "content": ContentModel.Config.schema_extra["example"],
                "topics": ["test-topic", "test-topic2"],
                "tag_text": ["tag1", ["tag2"]],
                "questions": ["60ad0fc9f0d053ea63e1645b"],
            }
        }


class QuestionModel(BaseEduModel):
    text: Optional[str]
    micro_lesson_id: Optional[PyObjectId]
    type: Optional[str]
    url: Optional[str]
    users_viewed: Optional[List[PyObjectId]]
    allow_user_suggest_answer: Optional[bool]
    has_correct_answer: Optional[bool]
    answers: Optional[List[AnswerModel]]
    labels: Optional[List[str]]
    tag_text: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "text": "Question 2",
                "micro_lesson_id": "60ad0fc9f0d053ea63e1645b",
                "type": "multiple_choice",
                "url": "url",
                "users_viewed": [
                    "60ad0fc9f0d053ea63e1645b",
                    "60ad0fc9f0d053ea63e1645c",
                ],
                "allow_user_suggest_answer": False,
                "has_correct_answer": True,
                "answers": [
                    AnswerModel.Config.schema_extra["example"],
                    AnswerModel.Config.schema_extra["example"],
                ],
                "tag_text": ["tag1", "tag2"],
                "labels": ["1", "100"],
            }
        }


class FullMicroLessonModel(MicroLessonModel):
    questions: Optional[List[QuestionModel]]

    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    QuestionModel.Config.schema_extra["example"],
                    QuestionModel.Config.schema_extra["example"],
                ],
            }
        }


class TutorialModel(BaseEduModel):
    title: Optional[str]
    description: Optional[str]
    goal: Optional[str]
    logo: Optional[str]
    min_age: Optional[int]
    max_age: Optional[int]
    tag_text: List[str] = []
    micro_lessons: Optional[List[PyObjectId]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60b775bec48c0b0013cb0e1f",
                "title": "Tutorial Python.",
                "description": "A very nice Tutorial description.",
                "goal": "string",
                "logo": "string",
                "min_age": 3,
                "max_age": 9,
                "tag_text": ["tag1", "tag2"],
                "micro_lessons": ["60ad0fc9f0d053ea63e1645b"],
            }
        }


class FullTutorialModel(TutorialModel):
    micro_lessons: Optional[List[MicroLessonModel]]


class CourseModel(BaseEduModel):
    title: Optional[str]
    rating: Optional[int]
    total_rating: Optional[int]
    users_rated: Optional[List[PyObjectId]]
    description: Optional[str]
    logo: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    navigation: Optional[str]
    time_to_complete: Optional[int]
    min_age: Optional[int]
    max_age: Optional[int]
    tag_text: List[str] = []
    tutorials: Optional[List[PyObjectId]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60b775d3c48c0b0013cb0e2a",
                "title": "Course Python.",
                "rating": 0,
                "total_rating": 0,
                "users_rated": [
                    "60ad0fc9f0d053ea63e1645b",
                    "60ad0fc9f0d053ea63e1645c",
                ],
                "description": "A very nice Course description.",
                "logo": "Logo",
                "start_date": "2021-07-06T13:47:43.207Z",
                "end_date": "2021-07-06T13:47:43.207Z",
                "navigation": "Navigation",
                "tag_text": ["tag_1", "tag2"],
                "time_to_complete": 0,
                "min_age": 3,
                "max_age": 9,
                "tutorials": ["60ad0fc9f0d053ea63e1645b"],
            }
        }


class FullCourseModel(CourseModel):
    tutorials: Optional[List[TutorialModel]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60b775d3c48c0b0013cb0e2a",
                "title": "Course Python.",
                "rating": 0,
                "total_rating": 0,
                "users_rated": [
                    "60ad0fc9f0d053ea63e1645b",
                    "60ad0fc9f0d053ea63e1645c",
                ],
                "description": "A very nice Course description.",
                "logo": "Logo",
                "start_date": "2021-07-06T13:47:43.207Z",
                "end_date": "2021-07-06T13:47:43.207Z",
                "navigation": "Navigation",
                "tutorials": [
                    TutorialModel.Config.schema_extra["example"],
                    TutorialModel.Config.schema_extra["example"],
                ],
                "tag_text": ["tag_1", "tag2"],
                "time_to_complete": 0,
                "min_age": 3,
                "max_age": 9,
            }
        }


class SceneTemplateModel(BaseEduModel):
    type: Optional[str]
    name: str
    description: str
    category: Optional[str]
    title: Optional[str]
    video_url: Optional[str]
    parameters: Optional[Dict]
    tag_text: Optional[List[str]]
    preview: Optional[str]
    evaluation_scheme: Optional[str] = ""
    format: Optional[str] = ""

    class Config:
        schema_extra = {
            "example": {
                "type": "react ",
                "name": "base",
                "description": "template",
                "category": "",
                "video_url": "url",
                "parameters": {},
                "tag_text": ["tag1"],
                "preview": "",
                "evaluation_scheme": "",
            }
        }


class SceneModel(BaseEduModel):
    scene_template_id: Optional[SceneTemplateModel]
    language_id: Optional[str]
    parameter_values: Optional[Dict]
    title: Optional[str]
    preview: Optional[str]
    tag_text: List[str] = []
    age_group: Optional[AgeGroup]
    format: Optional[str] = ""

    class Config:
        schema_extra = {
            "example": {
                "scene_template_id": SceneTemplateModel.Config.schema_extra[
                    "example"
                ],
                "language_id": "60cb490952aa731a49777d6d",
                "parameter_values": {},
                "title": "Title",
                "preview": "",
                "tag_text": ["tag1", "tag2"],
            }
        }


class ColoringSceneModel(BaseEduModel):
    scene_template_id: Optional[SceneTemplateModel]
    language_id: Optional[str]
    parameter_values: Optional[Dict]
    title: Optional[str]
    preview: Optional[str]
    tag_text: List[str] = []
    format: Optional[str] = ""

    class Config:
        schema_extra = {
            "example": {
                "scene_template_id": SceneTemplateModel.Config.schema_extra[
                    "example"
                ],
                "language_id": "60cb490952aa731a49777d6d",
                "parameter_values": {},
                "title": "Title",
                "preview": "",
                "tag_text": ["tag1"],
            }
        }


class GoalModel(BaseEduModel):
    deleted: bool
    text: Optional[str]

    class Config:
        schema_extra = {
            "example": {"deleted": False, "text": "A very nice text."}
        }


class LearnPathModel(BaseEduModel):
    title: Optional[str]
    description: Optional[str]
    tag_text: Optional[List[str]]
    goal: Optional[GoalModel]
    logo: Optional[str]
    min_age: Optional[int]
    max_age: Optional[int]
    scenes: Optional[List[PyObjectId]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60e80ae5dfe979418a39f3fb",
                "title": "First Learn Path",
                "description": "A very nice LearnPath description.",
                "tag_text": ["tag1"],
                "goal": GoalModel.Config.schema_extra["example"],
                "logo": "string",
                "min_age": 3,
                "max_age": 10,
                "scenes": ["60cb490952aa731a49777d6d"],
            }
        }


class FullLearnPathModel(LearnPathModel):
    scenes: Optional[List[SceneModel]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60e80ae5dfe979418a39f3fb",
                "scenes": [
                    SceneModel.Config.schema_extra["example"],
                    SceneModel.Config.schema_extra["example"],
                ],
                "title": "First Learn Path",
                "description": "A very nice LearnPath description.",
                "tag_text": ["tag1"],
                "goal": GoalModel.Config.schema_extra["example"],
                "logo": "string",
                "min_age": 3,
                "max_age": 10,
            }
        }


class StoryPage(BaseModel):
    scene_id: Optional[PyObjectId]
    title: Optional[str]
    text: Optional[Union[str, List[str]]]
    tips: Optional[List[str]]
    image_url: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "scene_id": "60e80ae5dfe979418a39f3fb",
                "title": "First Learn Path",
                "text": "A very nice StoryPage description.",
                "tips": ["tag1"],
                "image_url": "string",
            }
        }


class FullStoryPage(StoryPage):
    scene_id: Optional[SceneModel]

    class Config:
        schema_extra = {
            "example": {
                "scene_id": SceneModel.Config.schema_extra["example"],
                "title": "First Learn Path",
                "text": "A very nice LearnPath description.",
                "tips": ["tips 1"],
                "image_url": "string",
            }
        }


class StoryModel(BaseEduModel):
    title: str
    logo: Optional[str]
    tag_text: Optional[List[str]]
    language_id: Optional[str]
    pages: Optional[List[StoryPage]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60eed8a8d96f846a39d6edc6",
                "title": "Story 1",
                "logo": "http://placeimg.com/640/480",
                "tag_text": ["tag1"],
                "pages": [
                    {
                        "scene_id": "60eed8a8d96f846a39d6edc6",
                        "text": "story1",
                    },
                ],
            }
        }


class FullStoryModel(StoryModel):
    pages: Optional[List[FullStoryPage]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60eed8a8d96f846a39d6edc6",
                "title": "Story 1",
                "logo": "http://placeimg.com/640/480",
                "pages": [
                    {
                        "scene_id": {
                            "scene_template_id": (
                                SceneTemplateModel.Config.schema_extra[
                                    "example"
                                ]
                            ),
                            "language_id": "60cb490952aa731a49777d6d",
                            "parameter_values": {},
                            "title": "Title",
                            "preview": "",
                            "tag_text": ["tag1"],
                        },
                        "text": "story1",
                    },
                ],
                "tag_text": ["tag1"],
            }
        }


class ExerciseModel(BaseEduModel):
    org_id: str
    title: str
    tag_text: Optional[List[str]]
    min_age: Optional[int]
    max_age: Optional[int]
    category: str
    is_active: bool
    created_at: datetime
    scenes: Optional[List[PyObjectId]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60e80ae5dfe979418a39f3fb",
                "title": "First Learn Path",
                "category": "Category.",
                "tag_text": ["tag1"],
                "logo": "string",
                "min_age": 3,
                "max_age": 10,
                "created_at": "2022-01-01T12:00:00",
                "is_active": True,
                "scenes": ["60eed8a8d96f846a39d6edc6"],
            }
        }


class FullExerciseModel(ExerciseModel):
    scenes: Optional[List[SceneModel]]

    class Config:
        schema_extra = {
            "example": {
                "_id": "60e80ae5dfe979418a39f3fb",
                "count_scenes": 1,
                "title": "First Learn Path",
                "category": "Category.",
                "tag_text": ["tag1"],
                "logo": "string",
                "min_age": 3,
                "max_age": 10,
                "created_at": "2022-01-01T12:00:00",
                "is_active": True,
                "scenes": [
                    SceneModel.Config.schema_extra["example"],
                ],
            }
        }


class PaginationModel(BaseModel):
    total: int
    count: int
    page_num: int
    page_size: int
    results: Any

    class Meta:
        schema_extra = {
            "example": {
                "total": 10,
                "page_size": 10,
                "page_num": 1,
                "results": [],
            }
        }

    class Config:
        json_encoders = {ObjectId: str}


class ScenePaginatedResult(PaginationModel):
    results: List[SceneModel]


class ColoringScenePaginatedResult(PaginationModel):
    results: List[ColoringSceneModel]


class LearnPathPaginatedResult(PaginationModel):
    results: List[LearnPathModel]


class GroupPaginatedResult(PaginationModel):
    results: List[GroupModel]


class StoryPaginatedResult(PaginationModel):
    results: List[StoryModel]


class ExercisesPaginatedResult(PaginationModel):
    results: List[ExerciseModel]
