from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from pydantic.v1 import (
    BaseModel,
    Field,
)


class Proposal(BaseModel):
    proposal_id: str = ""
    person_id: str = ""
    type: str = ""
    code: str = ""
    number: str = ""
    title: str = ""


class Lims(BaseModel):
    name: str = ""
    description: str = ""


class Session(BaseModel):
    session_id: str = ""
    beamline_name: str = ""
    start_date: str = ""  # YYYYMDD
    start_time: str = ""
    end_date: str = ""  # YYYYMDD
    end_time: str = ""

    # Proposal information
    title: str = ""
    code: str = ""
    number: str = ""
    proposal_id: str = ""
    proposal_name: str = ""

    comments: Optional[str] = ""

    start_datetime: datetime = Field(default_factory=datetime.now)
    end_datetime: Optional[datetime] = Field(
        default_factory=lambda: datetime.now() + timedelta(days=1)
    )

    # If rescheduled the actual dates are used instead
    actual_start_date: str = ""
    actual_start_time: str = ""
    actual_end_date: str = ""
    actual_end_time: str = ""

    nb_shifts: str = ""
    scheduled: str = ""

    # status of the session depending on wether it has been rescheduled or moved
    is_rescheduled: bool = False
    is_scheduled_time: bool = False
    is_scheduled_beamline: bool = False

    # direct links to different services
    user_portal_URL: Optional[str] = None
    data_portal_URL: Optional[str] = None
    logbook_URL: Optional[str] = None

    volume: Optional[str] = None
    dataset_count: Optional[str] = None
    sample_count: Optional[str] = None


class Instrument(BaseModel):
    name: str
    id: int
    instrumentScientists: List[Any]


class Investigation(BaseModel):
    name: str
    startDate: datetime
    endDate: datetime
    id: int
    title: str
    visitId: str
    summary: str
    parameters: Dict[str, Any]
    instrument: Instrument
    investigationUsers: List[Any]


class Parameter(BaseModel):
    name: str
    value: str
    id: int
    units: str


class MetaPage(BaseModel):
    totalWithoutFilters: int
    total: int
    totalPages: int
    currentPage: int


class Meta(BaseModel):
    page: MetaPage


class LimsUser(BaseModel):
    user_name: str = ""
    sessions: Optional[List[Session]] = []


class LimsSessionManager(BaseModel):
    active_session: Optional[Session] = None
    sessions: Optional[List[Session]] = []
    users: Optional[Dict[str, LimsUser]] = {}


class SampleSheet(BaseModel):
    id: int
    name: str
    investigation: Investigation
    modTime: datetime
    parameters: List[Parameter]
    datasets: List[Any]
    meta: Meta
