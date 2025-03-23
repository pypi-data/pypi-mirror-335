Usage:
from pyecharts_json_render import render
jsn = render.read_json_file('./TEST_JSON.json')
render.render_html_from_ec_option_json(jsn)

option = render.pyecharts_html_to_echarts_option(html)
render.render_html_from_ec_option_json(option)