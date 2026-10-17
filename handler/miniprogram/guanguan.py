from handler.basehandler import BaseHandler
from service.common.page_copy import list_page_copy
from service.common.profile_board import ProfileBoardService
from service.guanguan import GuanguanService, UNKNOWN_NEGATIVE_ONE
from util.monitor import superMonitor, Response
from util.time_cost import timecost


class GuanguanHandler(BaseHandler):

    @superMonitor
    @timecost
    def get(self):
        longitude = self.getRequestParameter('longitude', default=UNKNOWN_NEGATIVE_ONE, paraType=float)
        latitude = self.getRequestParameter('latitude', default=UNKNOWN_NEGATIVE_ONE, paraType=float)
        limit = self.getRequestParameter('limit', paraType=int, default=20)

        ggs = GuanguanService(self.currentPassportId)
        config_sufficient = ProfileBoardService.info_is_filled(self.currentPassportId) if self.currentPassportId else False

        return Response(data={
            "guanguanList": ggs.getGuanguanList(longitude, latitude, limit),
            "configSufficient": config_sufficient,
            "copy": list_page_copy(),
        })
