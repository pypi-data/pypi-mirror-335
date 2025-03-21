from python_snoo.containers import BabyData
from python_snoo.exceptions import SnooBabyError
from python_snoo.snoo import Snoo


class Baby:
    def __init__(self, baby_id: str, snoo: Snoo):
        self.baby_id = baby_id
        self.snoo = snoo
        self.baby_url = f"https://api-us-east-1-prod.happiestbaby.com/us/me/v10/babies/{self.baby_id}"

    @property
    def session(self):
        return self.snoo.session

    async def get_status(self) -> BabyData:
        hdrs = self.snoo.generate_snoo_auth_headers(self.snoo.tokens.aws_id)
        try:
            r = await self.session.get(self.baby_url, headers=hdrs)
            resp = await r.json()
        except Exception as ex:
            raise SnooBabyError from ex
        return BabyData.from_dict(resp)
