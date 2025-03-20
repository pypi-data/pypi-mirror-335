import json

from cobweb import setting
from cobweb.base import BaseItem
from cobweb.pipelines import Pipeline
from aliyun.log import LogClient, LogItem, PutLogsRequest


class Loghub(Pipeline):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = LogClient(**setting.LOGHUB_CONFIG)

    def build(self, item: BaseItem):
        log_item = LogItem()
        temp = item.to_dict
        for key, value in temp.items():
            if not isinstance(value, str):
                temp[key] = json.dumps(value, ensure_ascii=False)
        contents = sorted(temp.items())
        log_item.set_contents(contents)
        return log_item

    def upload(self, table, datas):
        request = PutLogsRequest(
            project=setting.LOGHUB_PROJECT,
            logstore=table,
            topic=setting.LOGHUB_TOPIC,
            source=setting.LOGHUB_SOURCE,
            logitems=datas,
            compress=True
        )
        self.client.put_logs(request=request)
