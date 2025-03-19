import json

from oschart import os_chart_db, OsChart
from oschart.utils.field_info import FIELD_SETTINGS, SOCIAL_PAGE_SUMMARY

db_mysql = {
    'host': '47.93.161.10',
    'port': 4000,
    'user': 'onesight_dev',
    'password': '%hv$J%8lJTkXfHIB$cWb',
    'db': 'Intelligence',
    'charset': 'utf8mb4',
    'pre': 'pre_'
}

db_es = {
    "host": "es-cn-tl32se3nv001vj1rx.public.elasticsearch.aliyuncs.com",
    "port": "9200",
    "user": "elastic",
    "password": "1SightUpEs",
}

db_const = {
    'db_mysql': db_mysql,
    'db_es': db_es
}


os_chart_db.set_mysql_config(
        host=db_mysql["host"],
        port=db_mysql["port"],
        user=db_mysql["user"],
        password=db_mysql["password"],
        database=db_mysql["db"],
    )
# os_charts es
os_chart_db.set_es_config(
        host=db_es["host"],
        port=db_es["port"],
        user=db_es["user"],
        password=db_es["password"],
    )

if __name__ == "__main__":
    for k in list(SOCIAL_PAGE_SUMMARY.keys()):
        obj = OsChart(
            date_start="2024-01-10",
            date_end="2025-01-15",
            filed_key=[k],
            page_id="228583470",
            platform="vkontakte",
            date_type="day",
        )
        print(json.dumps(obj.get_chart_data_for_os()))

