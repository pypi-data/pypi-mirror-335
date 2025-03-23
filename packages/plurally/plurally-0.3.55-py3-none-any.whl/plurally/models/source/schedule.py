import re
from datetime import datetime, timezone

import pytz
from croniter import croniter
from loguru import logger
from pydantic import Field, field_validator
from pydantic_extra_types.timezone_name import TimeZoneName, timezone_name_settings

from plurally.json_utils import load_from_json_dict
from plurally.models.node import Node


@timezone_name_settings(strict=False)
class TZNonStrict(TimeZoneName):
    pass


class Schedule(Node):
    ICON = "schedule"
    IS_TRIGGER = True

    class InitSchema(Node.InitSchema):
        """Schedule the execution of the flow using a cron string."""

        cron_string: str = Field(
            title="Schedule",
            description="When the flow should be triggered.",
            json_schema_extra={
                "default-show": "Every day at 18:00",
                "auto:default": "cron_string:0 18 * * *",
                "uiSchema": {
                    "ui:widget": "CronWidget",
                },
            },
            examples=[
                "Every week on monday at 18:00",
                "Every day at 18:00",
                "Every hour",
            ],
        )

        timezone: TZNonStrict = Field(
            title="Timezone",
            description="The timezone to use for the schedule.",
            json_schema_extra={
                "advanced": True,
                "auto:default": "local-tz",
            },
        )

        @field_validator("cron_string", mode="after")
        def validate_cron_string(cls, value):
            minute_str = value.split(" ")[0].strip()
            if minute_str == "*":
                raise ValueError("The minumum interval is 15 minutes")
            every = re.match(r"^\*\/\d+$", minute_str)
            if every and int(minute_str[2:]) < 15:
                raise ValueError("The minumum interval is 15 minutes")

            minutes = re.findall(r"\d+", minute_str)
            if minutes and len(minutes) > 1:
                minutes = sorted([int(m) for m in minutes])
                diffs = [minutes[i] - minutes[i - 1] for i in range(1, len(minutes))]
                last_diff = minutes[0] + 60 - minutes[-1]
                diffs.append(last_diff)
                if not all(diff >= 15 for diff in diffs):
                    raise ValueError("The minumum interval is 15 minutes")
            return value

    class InputSchema(Node.InputSchema):
        pass

    class OutputSchema(Node.OutputSchema):
        execution_time: datetime = Field(
            title="Execution Time",
            description="The time when the schedule is triggered.",
            format="date-time",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        self.cron_string = init_inputs.cron_string
        self.last_exec = datetime.now(tz=timezone.utc).replace(tzinfo=None)  # last_exec is always utc not timezone aware
        self.timezone = init_inputs.timezone
        super().__init__(init_inputs)

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value: TZNonStrict):
        self._timezone = pytz.timezone(value)

    @property
    def localized_last_exec(self):
        return self.last_exec.replace(tzinfo=pytz.utc).astimezone(self.timezone)

    @property
    def next(self):
        # init cron string with localized_last_exec
        cron = croniter(self.cron_string, self.localized_last_exec)
        # next is always utc not timezone aware
        # careful: this is iter, do not call get_next multiple times
        return cron.get_next(datetime).astimezone(timezone.utc).replace(tzinfo=None)

    def should_run(self, now: datetime):
        return now >= self.next

    def now(self):
        return datetime.now(tz=timezone.utc).replace(tzinfo=None)

    def forward(self, _: InputSchema):
        now = self.now()
        if self.should_run(now):
            self.last_exec = now
            now_aware = now.replace(tzinfo=timezone.utc).astimezone(self.timezone)
            logger.debug(f"Schedule {self.name} triggered at {now_aware}")
            self.outputs = {"execution_time": now_aware}
        else:
            self.outputs = None

    def serialize(self):
        return super().serialize() | {
            "cron_string": self.cron_string,
            "timezone": self.timezone.zone,
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        kwargs["timezone"] = TZNonStrict(kwargs["timezone"])
        schedule = cls(cls.InitSchema(**kwargs))
        return schedule
