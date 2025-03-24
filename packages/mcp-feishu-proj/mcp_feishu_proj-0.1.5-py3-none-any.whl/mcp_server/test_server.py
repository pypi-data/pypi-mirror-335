#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
飞书项目MCP服务器测试
"""

import unittest
# 使用绝对导入而不是相对导入，以便在 unittest discover 时正确导入
from src.mcp_server.server import get_view_list, get_view_detail, get_work_item_detail, get_work_item_type_meta

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

    def test_get_work_item_detail(self):
        """测试获取工作项详情功能"""
        print("\n===== 测试 get_work_item_detail =====")
        try:
            # 首先获取视图列表
            view_list = get_view_list("story")
            self.assertIsNotNone(view_list, "视图列表不应为None")
            self.assertTrue(len(view_list) > 0, "视图列表不应为空")
            
            # 遍历视图列表，寻找包含工作项的视图
            work_item_ids = []
            view_detail = None
            view_id = None
            
            for view in view_list:
                view_id = view["view_id"]
                print(f"尝试使用视图ID: {view_id}")
                
                view_detail = get_view_detail(view_id)
                self.assertIsNotNone(view_detail, "视图详情不应为None")
                
                # 从视图详情中获取工作项ID
                work_item_ids = view_detail.get("work_item_id_list", [])
                if work_item_ids:
                    print(f"找到包含工作项的视图: {view_id}")
                    break
                else:
                    print(f"视图 {view_id} 中没有工作项，尝试下一个视图")
            
            # 如果所有视图都没有工作项，则跳过测试
            if not work_item_ids:
                print("所有视图中都没有工作项，跳过测试")
                return
            
            # 获取前两个工作项的ID（如果有的话）
            work_item_ids = [str(id) for id in work_item_ids[:2]]
            if not work_item_ids:
                print("无法获取工作项ID，跳过测试")
                return
            
            work_item_ids_str = ",".join(work_item_ids)
            print(f"使用工作项ID: {work_item_ids_str}")
            
            # 调用get_work_item_detail函数
            work_item_details = get_work_item_detail("story", work_item_ids_str)
            self.assertIsNotNone(work_item_details, "工作项详情不应为None")
            
            # 验证返回的工作项数量与请求的ID数量一致
            self.assertEqual(len(work_item_details), len(work_item_ids), 
                            f"返回的工作项数量({len(work_item_details)})应与请求的ID数量({len(work_item_ids)})一致")
            
            # 验证每个工作项的ID与请求的ID一致
            for detail in work_item_details:
                self.assertIn("id", detail, "工作项详情中应包含id字段")
                self.assertIn(str(detail["id"]), work_item_ids, 
                             f"返回的工作项ID {detail['id']} 应在请求的ID列表中")
            
            print(f"获取到工作项详情，共 {len(work_item_details)} 个工作项")
        except Exception as e:
            self.fail(f"测试 get_work_item_detail 失败: {str(e)}")
    
    def test_get_work_item_type_meta(self):
        """测试获取工作项类型元数据功能"""
        print("\n===== 测试 get_work_item_type_meta =====")
        try:
            # 测试获取需求类型的元数据
            work_item_type_meta = get_work_item_type_meta("story")
            self.assertIsNotNone(work_item_type_meta, "工作项类型元数据不应为None")
            
            # 验证元数据是一个列表
            self.assertIsInstance(work_item_type_meta, list, "工作项类型元数据应为列表类型")
            self.assertTrue(len(work_item_type_meta) > 0, "工作项类型元数据列表不应为空")
            
            # 验证列表中的元素包含必要的字段
            first_field = work_item_type_meta[0]
            self.assertIsInstance(first_field, dict, "字段元素应为字典类型")
            self.assertIn("field_name", first_field, "字段元素中应包含field_name")
            self.assertIn("field_key", first_field, "字段元素中应包含field_key")
            
            print(f"获取到工作项类型元数据，包含 {len(work_item_type_meta)} 个字段")
            
            # 测试获取缺陷类型的元数据
            issue_meta = get_work_item_type_meta("issue")
            self.assertIsNotNone(issue_meta, "缺陷类型元数据不应为None")
            self.assertIsInstance(issue_meta, list, "缺陷类型元数据应为列表类型")
            self.assertTrue(len(issue_meta) > 0, "缺陷类型元数据列表不应为空")
            
            print(f"获取到缺陷类型元数据，包含 {len(issue_meta)} 个字段")
            
            # 测试获取版本类型的元数据
            version_meta = get_work_item_type_meta("version")
            self.assertIsNotNone(version_meta, "版本类型元数据不应为None")
            self.assertIsInstance(version_meta, list, "版本类型元数据应为列表类型")
            self.assertTrue(len(version_meta) > 0, "版本类型元数据列表不应为空")
            
            print(f"获取到版本类型元数据，包含 {len(version_meta)} 个字段")
        except Exception as e:
            self.fail(f"测试 get_work_item_type_meta 失败: {str(e)}")

if __name__ == "__main__":
    unittest.main()
