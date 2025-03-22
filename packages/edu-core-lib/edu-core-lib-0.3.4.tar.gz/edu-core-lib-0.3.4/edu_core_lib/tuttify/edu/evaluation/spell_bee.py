"""
The goal is
1. The logic of the evaluation will be in a class specific to this evaluation
scheme.
2. New evaluation scheme can be added anytime.
3. Airflow jobs run every night to analyse all the interactions of the day for
scenes associated with a scene template which has an evaluation scheme
attached to it. based on the evaluation scheme the interactions will be
evaluated and grades is created and stored for the student.
"""
import datetime
from statistics import median

import numpy as np
import pandas as pd
from bson import ObjectId

from edu_core_lib.tuttify.edu.adapters import MongoDataAdapterClass
from edu_core_lib.tuttify.edu.constants import (
    AVERAGE,
    EXCELLENT,
    GOOD,
    NEED_HELP,
    QUARTILE,
    SOLVED_SCENE,
    STARTED_SCENE,
)


class NotFoundSceneException(BaseException):
    ...


class SpellBeeEvalScheme:
    name = "spell_bee_eval_scheme"
    start_interaction = STARTED_SCENE
    solved_interaction = SOLVED_SCENE

    def __init__(self, user_id, org_id, logger=None, extra=None):
        self.user_id = user_id
        self.org_id = org_id
        self.total_timespent = {}
        self.result_per_word = {}
        self.quantile = {}
        self._scene_analytics = {}
        self.recent_interactions = {}
        self.logger = logger
        self.extra = extra or {}

    def get_data(self):
        raise NotImplementedError

    def analyze(self):
        self.logger.info(
            "Start analyze spell bee interactions", extra=self.extra
        )
        data = self.get_data()
        self.logger.info(f"Found data: {data}", extra=self.extra)
        if not data:
            return {}
        self.create_users_analytics(data)
        result = self.check_user_result()
        return result

    def create_users_analytics(self, data):
        for scene in data:
            scene_id = scene["_id"]
            self.logger.info(f"Process scene {scene_id}")
            try:
                scene_obj = self.get_scene_by_id(scene_id)
            except NotFoundSceneException:
                self.logger.info(
                    f"Not found scene {scene_id}", extra=self.extra
                )
                continue

            total_time = self._fetch_scene_analytics(scene_id)
            word = (
                scene_obj.get("parameter_values", {})
                .get("config", {})
                .get("items", {})
                .get("value")
            )

            if not word:
                self.logger.info(
                    f"Not found valid parameters for scene {scene_id}",
                    extra=self.extra,
                )
                continue

            word_len = scene_obj.get("parameter_values", {}).get(
                "config", {}
            ).get("items", {}).get("value_length") or len(word)
            self.logger.info(
                f"Analyze word {word}, {word_len} letters", extra=self.extra
            )
            self.total_timespent[word_len] = []
            self.result_per_word[word_len] = []
            if total_time:
                self.total_timespent[word_len].append(total_time)

            df = pd.DataFrame(scene["interactions"])
            df["datetime"] = pd.to_datetime(df.created_at)
            try:
                df["is_correct"] = df.apply(
                    lambda row: row["data"]
                    .get("params", {})
                    .get("isCorrect", None),
                    axis=1,
                )
            except KeyError:
                continue
            if df.empty:
                continue

            df_diff = (
                df.groupby(by=["entity_id"])
                .apply(self.process_interactions)
                .reset_index()
            )
            res = {
                "correct": {"diff": [], "count": 0},
                "wrong": {"diff": [], "count": 0},
            }
            for row in df_diff.iterrows():
                for r in row[1].result:
                    if r[1] is True:
                        field = "correct"
                    else:
                        field = "wrong"
                    res[field]["diff"].append(r[0])
                    res[field]["count"] += 1

            res["correct"]["diff"].sort()
            res["wrong"]["diff"].sort()

            word_median = (
                median(res["correct"]["diff"])
                if res["correct"]["diff"]
                else None
            )

            created_at = datetime.datetime.fromisoformat(
                scene["interactions"][-1]["created_at"]
            )
            result = {
                "word": word,
                "attempts": len(
                    df[df.interaction_type == "user_started_scene"].index
                ),
                "correct_attempts": res["correct"]["count"],
                "time_per_correct": word_median,
                "total_timespent": sum(res["correct"]["diff"]),
                "last_interaction_time": created_at,
            }

            self.recent_interactions[created_at] = {
                "word": word,
                "mdn_t": word_median,
            }
            self.result_per_word[word_len].append(result)

        for word_len in range(3, 13):
            self.quantile[word_len] = (
                list(np.quantile(self.total_timespent[word_len], QUARTILE))
                if self.total_timespent.get(word_len)
                else None
            )

    def process_interactions(self, group_):
        result = []
        started = None
        prev = None
        group = group_.sort_values("datetime")
        for r in group.iterrows():
            r = r[1]
            if r.interaction_type == self.start_interaction:
                started = r.datetime
            if (
                r.interaction_type == self.start_interaction
                and prev == self.start_interaction
            ):
                continue
            if r.interaction_type == self.solved_interaction:
                completed = r.datetime
                if not started:
                    continue
                diff = completed - started
                if diff > datetime.timedelta(hours=1):
                    started = None
                    prev = r.interaction_type
                    continue

                result.append((diff.total_seconds(), r.is_correct))
                started = None
            prev = r.interaction_type

        return pd.Series((result,), index=["result"])

    def _fetch_scene_analytics(self, scene_id):
        analytics = self._data_adapter.get_data(
            "content_analytics_summary",
            [{"$match": {"content_id": scene_id, "content_type": "scene"}}],
        )
        if not analytics:
            self.logger.info(
                f"Not found analyze for scene {scene_id}", extra=self.extra
            )
            return None
        self.logger.info(
            f"Found scene summary {analytics[0]}", extra=self.extra
        )
        total_time = (
            analytics[0]
            .get("analytics", {})
            .get("spelling_analytics", {})
            .get("time", {})
            .get("total", {})
        )
        self.logger.info(f"Time median is {total_time}", extra=self.extra)
        return total_time

    def check_user_result(self):
        words_analytics = []
        for word_len in range(3, 13):
            correct_attempts, attempts, total_time = [], [], []
            for word in self.result_per_word.get(word_len, []) or []:
                if word.get("correct_attempts") < 0:
                    continue
                correct_attempts.append(word.get("correct_attempts"))
                attempts.append(word.get("attempts"))
                total_time.append(word.get("total_timespent"))
            total_attempts = sum(attempts)
            if total_attempts:
                percent_correct = (
                    sum(correct_attempts) / total_attempts
                ) * 100
                total_median = median(total_time)
            else:
                percent_correct = None
                total_median = None
            if (
                percent_correct
                and total_median
                and self.quantile.get(word_len)
            ):
                result = self.calculate_result(
                    word_len, percent_correct, total_median
                )
            else:
                result = "Not enough data"
            words_analytics.append(
                {
                    "length": word_len,
                    "per_correct": percent_correct,
                    "mdn_t": total_median,
                    "result": result,
                }
            )
        recent_words = self.get_recent_words()
        return {
            "words_analytics": words_analytics,
            "recent_words": recent_words,
        }

    def calculate_result(self, word_len, percent_correct, total_median):
        if percent_correct < 50:
            return NEED_HELP
        elif 50 <= percent_correct < 75:
            if total_median < self.quantile[word_len][0]:
                return EXCELLENT
            elif (
                self.quantile[word_len][0]
                <= total_median
                < self.quantile[word_len][1]
            ):
                return GOOD
            else:
                return AVERAGE
        elif percent_correct <= 75:
            if total_median < self.quantile[word_len][2]:
                return EXCELLENT
            else:
                return GOOD

    def get_recent_words(self):
        keys = list(self.recent_interactions.keys())
        keys.sort(reverse=True)
        latest_three = keys[0:3]
        result = []
        for dt in latest_three:
            word = self.recent_interactions[dt]
            word_len = len(word["word"])

            result.append(
                {
                    **word,
                    "Q1": self.quantile[word_len][0]
                    if self.quantile.get(word_len)
                    else None,
                    "Q2": self.quantile[word_len][1]
                    if self.quantile.get(word_len)
                    else None,
                    "Q3": self.quantile[word_len][2]
                    if self.quantile.get(word_len)
                    else None,
                }
            )
        return result

    def get_scene_by_id(self, scene_id):
        scenes = self._data_adapter.get_data(
            "scenemodels",
            [{"$match": {"_id": ObjectId(scene_id)}}],
        )
        if not scenes:
            raise NotFoundSceneException
        return scenes[0]


class MongoSpellBeeEvalScheme(SpellBeeEvalScheme):
    _data_adapter: MongoDataAdapterClass

    def __init__(
        self, data_adapter: MongoDataAdapterClass, user_id, org_id, **kwargs
    ):
        self._data_adapter = data_adapter
        super().__init__(user_id, org_id, **kwargs)

    def get_data(self):
        result = self._data_adapter.get_data(
            "studentinteractions",
            [
                {
                    "$match": {
                        "user_id": self.user_id,
                        "org_id": self.org_id,
                        "data.evaluation_scheme": self.name,
                    }
                },
                {
                    "$group": {
                        "_id": "$entity_id",
                        "interactions": {"$push": "$$ROOT"},
                    }
                },
            ],
        )
        return result
