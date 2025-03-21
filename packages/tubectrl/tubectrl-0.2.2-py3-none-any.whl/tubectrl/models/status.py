from typing import Literal

from pydantic import BaseModel, Field


class Status(BaseModel):
    uploadStatus: Literal["deleted", "failed", "processed", "rejected", "uploaded"]
    failureReason: Literal[
        "codec", "conversion", "invalidFile", "tooSmall", "uploadAborted"
    ]
    rejectionReason: Literal[
        "claim",
        "copyright",
        "duplicate",
        "inappropriate",
        "length",
        "termsOfUse",
        "trademark",
        "uploaderAccountClosed",
        "uploaderAccountSuspended",
    ]
    privacyStatus: Literal["private", "unlisted", "public"]
    publishAt: str
    failureReason: Literal["creativeCommon", "youtube"]
    embeddable: bool
    publicStatsViewable: bool
    madeForKids: bool
    selfDeclaredMadeForKids: bool
    containsSyntheticMedia: bool
