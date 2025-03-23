from plurally.models import (
    calendar,  # noqa: F403
    crm,  # noqa: F403
    email,  # noqa: F403
    eshop,  # noqa: F403
    files,  # noqa: F403
    instagram,  # noqa: F403
    logic,  # noqa: F403
    output,  # noqa: F403
    table,  # noqa: F403
    triggers,  # noqa: F403
)
from plurally.models.action import (
    ai,  # noqa: F403
    arithmetic,  # noqa: F403
    format,  # noqa: F403
)
from plurally.models.action.ai import *  # noqa: F403
from plurally.models.action.arithmetic import *  # noqa: F403
from plurally.models.action.format import *  # noqa: F403
from plurally.models.crm import *  # noqa: F403
from plurally.models.email import *  # noqa: F403
from plurally.models.form import *  # noqa: F403
from plurally.models.hs import hubspot_crm  # noqa: F403
from plurally.models.instagram import *  # noqa: F403
from plurally.models.logic import *  # noqa: F403
from plurally.models.meta import *  # noqa: F403
from plurally.models.misc import AudioFile  # noqa: F401
from plurally.models.node import Node, get_inner_type  # noqa: F401
from plurally.models.ol import overloop_crm  # noqa: F403
from plurally.models.output import *  # noqa: F403
from plurally.models.sf import salesforce_crm  # noqa: F403
from plurally.models.sf.salesforce_crm import *  # noqa: F403
from plurally.models.source import (
    constant,  # noqa: F403
    internet,  # noqa: F403
)
from plurally.models.source.chrome import *  # noqa: F403
from plurally.models.source.constant import *  # noqa: F403
from plurally.models.source.email_imap import *  # noqa: F403
from plurally.models.source.internet import *  # noqa: F403
from plurally.models.source.mic import *  # noqa: F403
from plurally.models.source.schedule import *  # noqa: F403
from plurally.models.table import *  # noqa: F403

GROUPS = [
    ("Triggers", triggers),
    ("AI", ai),
    ("Hubspot", hubspot_crm),
    ("Salesforce", salesforce_crm),
    ("CRM", crm),
    ("Overloop", overloop_crm),
    ("Email", email),
    ("Instagram", instagram),
    ("Data", table),
    ("Files", files),
    ("Scraping", internet),
    ("Calendar", calendar),
    ("Eshop", eshop),
    ("Transforms & Validators", format),
    ("Constant Value", constant),
    ("Logic", logic),
    ("Maths", arithmetic),
    ("Output", output),
]

# This is a hack to avoid circular imports
from plurally.models.flow import Flow  # noqa: F401, E402
from plurally.models.subflow import Subflow  # noqa: F401, E402
