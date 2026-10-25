from handler.basehandler import BaseHandler
from service.common.page_copy import list_page_copy
from service.common.presence import remember_location
from service.common.profile_board import ProfileBoardService
from service.guanguan import GuanguanService, UNKNOWN_NEGATIVE_ONE
from service.phone_bind import PhoneBindService
from util.const.match import (
    GUANGUAN_LIST_DEFAULT_LIMIT, GUANGUAN_LIST_MAX_LIMIT,
    LATITUDE_MAX, LATITUDE_MIN, LONGITUDE_MAX, LONGITUDE_MIN,
)
from util.monitor import superMonitor, Response
from util.time_cost import timecost


class GuanguanHandler(BaseHandler):

    @superMonitor
    @timecost
    def get(self):
        longitude = self.getFloatParameter(
            'longitude', default=UNKNOWN_NEGATIVE_ONE, minimum=LONGITUDE_MIN, maximum=LONGITUDE_MAX)
        latitude = self.getFloatParameter(
            'latitude', default=UNKNOWN_NEGATIVE_ONE, minimum=LATITUDE_MIN, maximum=LATITUDE_MAX)
        limit = self.getIntParameter(
            'limit', default=GUANGUAN_LIST_DEFAULT_LIMIT, minimum=1, maximum=GUANGUAN_LIST_MAX_LIMIT)

        _remember_list_location(self.currentPassportId, latitude, longitude)
        ggs = GuanguanService(self.currentPassportId)
        config_sufficient = ProfileBoardService.info_is_filled(self.currentPassportId) if self.currentPassportId else False

        data = {
            "guanguanList": ggs.getGuanguanList(longitude, latitude, limit),
            "configSufficient": config_sufficient,
            "copy": list_page_copy(),
        }
        if self.currentPassportId:
            data["phoneBound"] = PhoneBindService().bound(self.currentPassportId)
        return Response(data=data)


def _remember_list_location(passport_id, latitude, longitude):
    if not passport_id or latitude == UNKNOWN_NEGATIVE_ONE or longitude == UNKNOWN_NEGATIVE_ONE:
        return
    remember_location(passport_id, latitude, longitude)
