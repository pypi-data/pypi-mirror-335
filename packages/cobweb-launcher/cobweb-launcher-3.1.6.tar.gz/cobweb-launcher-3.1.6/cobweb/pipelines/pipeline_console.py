from cobweb.base import ConsoleItem, logger
from cobweb.constant import LogTemplate
from cobweb.pipelines import Pipeline


class Console(Pipeline):

    def build(self, item: ConsoleItem):
        return {
            "seed": item.seed.to_dict,
            "data": item.to_dict
        }

    def upload(self, table, datas):
        for data in datas:
            parse_detail = LogTemplate.log_info(data["data"])
            if len(parse_detail) > 500:
                parse_detail = parse_detail[:500] + " ...\n" + " " * 12 + "-- Text is too long and details are omitted!"
            logger.info(LogTemplate.console_item.format(
                seed_detail=LogTemplate.log_info(data["seed"]),
                parse_detail=parse_detail
            ))
