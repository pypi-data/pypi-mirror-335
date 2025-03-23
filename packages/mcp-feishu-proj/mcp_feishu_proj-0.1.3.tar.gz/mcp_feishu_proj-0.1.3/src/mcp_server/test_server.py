#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
飞书项目MCP服务器测试
"""

import unittest
# 使用绝对导入而不是相对导入，以便在 unittest discover 时正确导入
from src.mcp_server.server import get_view_list, get_view_detail

class TestFSProjMCPServer(unittest.TestCase):
    """测试飞书项目MCP服务器工具函数"""
    
    def test_get_view_list(self):
        """测试获取视图列表功能"""
        print("\n===== 测试 get_view_list =====")
        try:
            view_list = get_view_list("story")
            self.assertIsNotNone(view_list, "视图列表不应为None")
            self.assertTrue(len(view_list) > 0, "视图列表不应为空")
            print(f"获取到视图列表，共 {len(view_list)} 个视图")
        except Exception as e:
            self.fail(f"测试 get_view_list 失败: {str(e)}")
    
    def test_get_view_detail(self):
        """测试获取视图详情功能"""
        print("\n===== 测试 get_view_detail =====")
        try:
            # 首先获取视图列表，然后使用第一个视图的ID进行测试
            view_list = get_view_list("story")
            self.assertIsNotNone(view_list, "视图列表不应为None")
            self.assertTrue(len(view_list) > 0, "视图列表不应为空")
            
            first_view = view_list[0]
            self.assertIn("view_id", first_view, "视图对象中应包含view_id字段")
            
            first_view_id = first_view["view_id"]
            print(f"使用视图ID: {first_view_id}")
            
            view_detail = get_view_detail(first_view_id)
            self.assertIsNotNone(view_detail, "视图详情不应为None")
            self.assertIn("view_id", view_detail, "视图详情中应包含view_id字段")
            self.assertEqual(view_detail["view_id"], first_view_id, "返回的视图ID应与请求的一致")
            
            print(f"获取到视图详情: {view_detail}")
        except Exception as e:
            self.fail(f"测试 get_view_detail 失败: {str(e)}")

if __name__ == "__main__":
    unittest.main()
