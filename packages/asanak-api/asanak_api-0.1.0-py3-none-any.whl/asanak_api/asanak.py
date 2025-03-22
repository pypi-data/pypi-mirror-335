import json

import requests

from .actions import Actions


class APIException(Exception):
    pass


class HTTPException(Exception):
    pass


class AsanakAPI(object):
    def __init__(
        self,
        api_key: str = "",
        username: str = "",
        password: str = "",
        version="v2rest",
    ):
        self.version = version
        self.host = f"sms.asanak.ir/webservice/{self.version}"
        self.username, self.password = (
            (username, password) if username and password else api_key.split(",")
        )
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "charset": "utf-8",
        }

    def _normalize_params(self, params={}):
        if isinstance(params, dict):
            return json.dumps(
                {"username": self.username, "password": self.password, **params}
            )
        elif isinstance(params, list):
            return json.dumps(
                {
                    "username": self.username,
                    "password": self.password,
                    "data": [param for param in params],
                }
            )
        else:
            return json.dumps(
                {
                    "username": self.username,
                    "password": self.password,
                    **params.__dict__,
                }
            )

    def _request(self, action, parameters={}):
        url = "https://" + self.host + "/" + action["name"]
        try:
            res = requests.post(url, headers=self.headers, data=parameters)
            content = res.content
            try:
                response = json.loads(content.decode())
                if res.status_code == 200:
                    response = {
                        "status": response["meta"][action["success_state_field"]],
                        "message": response["meta"]["message"],
                        "data": response["data"],
                    }
                else:
                    response = {
                        "status": res.status_code,
                        "message": response["meta"]["message"],
                        "data": response["data"],
                    }
                return response
            except ValueError as e:
                raise HTTPException(e)
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPException(e)

    def sms_send(self, params):
        return self._request(Actions.SENDSMS, self._normalize_params(params))

    def sms_template(self, params):
        return self._request(Actions.TEMPLATE, self._normalize_params(params))

    def sms_p2p(self, params):
        return self._request(Actions.P2P, self._normalize_params(params))

    def sms_status(self, params):
        res = self._request(Actions.STATUS, self._normalize_params(params))
        return res

    def sms_template_list(self):
        return self._request(Actions.TEMPLATELIST, self._normalize_params())

    def get_credit(self):
        return self._request(Actions.GETCREDEIT, self._normalize_params())

    def get_rial_credit(self):
        return self._request(Actions.GETRIALCREDIT, self._normalize_params())

    def __repr__(self):
        return "asanak.AsanakAPI({!r})".format(self.username)

    def __str__(self):
        return "asanak.AsanakAPI({!s})".format(self.username)
