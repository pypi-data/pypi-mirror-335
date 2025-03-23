from robot_base import log_util

from ..__init__ import request_ai, request_ai_vl


def setup_function():
    log_util.Logger("", "INFO")


def test_spark_pai():
    resp = request_ai(
        base_url="https://maas-api.cn-huabei-1.xf-yun.com/v1",
        api_key="sk-iLEDisFrODAk7z645a124b454aC340BbB522C369A318A0Ef",
        model="xopqwenqwq32b",
        system_prompt="",
        user_prompt="提示词：你是一位资深的内容营销专家，擅长写作病毒式传播的爆款文章，请为我分析以下热点新闻：梁建章建议取消中高考，将筛选压力推迟到工作或考研环节，这个建议有道理吗？。\n根据以上新闻，选择一个切入点，写一个微头条。要求：1. 考虑不同受众群体的兴趣点2. 避免人云亦云的观点3 观点要新颖独特，避免落入俗套。\n直接给出内容，不要解释。",
        code_block_extra_data={
            "code_map_id": "WnUuS-LKwEsCHXIe",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "大模型对话",
        },
    )
    print(resp)


def test_zhipuai_api():
    resp = request_ai(
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key="5207027892661a80ba7ee26ee2508d6f.PdurJcToAeP6szpx",
        model="glm-4-flash",
        system_prompt="",
        user_prompt="提示词：你是一位资深的内容营销专家，擅长写作病毒式传播的爆款文章，请为我分析以下热点新闻：梁建章建议取消中高考，将筛选压力推迟到工作或考研环节，这个建议有道理吗？。\n根据以上新闻，选择一个切入点，写一个微头条。要求：1. 考虑不同受众群体的兴趣点2. 避免人云亦云的观点3 观点要新颖独特，避免落入俗套。\n直接给出内容，不要解释。",
        code_block_extra_data={
            "code_map_id": "WnUuS-LKwEsCHXIe",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "大模型对话",
        },
    )
    print(resp)


def test_request_ai_vl():
    resp = request_ai_vl(
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key="5207027892661a80ba7ee26ee2508d6f.PdurJcToAeP6szpx",
        model="glm-4v-flash",
        system_prompt="",
        user_prompt="识别并返回图片中的文本",
        file_path=r"C:\Users\Administrator\Pictures\Screenshots\屏幕截图 2025-01-12 093648.png",
        code_block_extra_data={
            "code_map_id": "WnUuS-LKwEsCHXIe",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "大模型对话",
        },
    )
    print(resp)
