from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService, UNKNOWN_NEGATIVE_ONE
from service.myself import UserInfoService
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
        uis = UserInfoService(self.currentPassport)
        config_sufficient = not uis.userInfoNeedFilled() if self.currentPassportId else False

        return Response(data={
            "guanguanList": ggs.getGuanguanList(longitude, latitude, limit),
            "configSufficient": config_sufficient,
        })
