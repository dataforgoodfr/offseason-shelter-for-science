# coding: utf-8

from enum import IntEnum

class AppRejectionCode(IntEnum):
    FILE_TOO_BIG_FOR_SEEDING = 1
    INSUFFICIENT_SPACE = 2
    HTTP_404 = 3 # HTTP : Not found
    HTTP_403 = 4 # HTTP : Forbidden
    FETCH_FAILED = 5 # javascript fetch failure
    NOT_SUITABLE_FOR_BETA = 100000