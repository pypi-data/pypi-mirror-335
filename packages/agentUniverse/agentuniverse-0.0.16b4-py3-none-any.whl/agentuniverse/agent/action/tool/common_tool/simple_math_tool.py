# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: simple_math_tool.py


from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class AddTool(Tool):
    def execute(self, tool_input: ToolInput):
        input_params = tool_input.get_data('input')
        a, b = input_params.split(',')
        result = float(a) + float(b)
        return result


class SubtractTool(Tool):
    def execute(self, tool_input: ToolInput):
        input_params = tool_input.get_data('input')
        a, b = input_params.split(',')
        result = float(a) - float(b)
        return result


class MultiplyTool(Tool):
    def execute(self, tool_input: ToolInput):
        input_params = tool_input.get_data('input')
        a, b = input_params.split(',')
        result = float(a) * float(b)
        return result


class DivideTool(Tool):
    def execute(self, tool_input: ToolInput):
        input_params = tool_input.get_data('input')
        a, b = input_params.split(',')
        result = float(a) / float(b)
        return result
