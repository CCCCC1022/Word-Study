

# #测试单个基金

# from DrissionPage import WebPage
# import re
# import time

# page = WebPage()
# code = "000366"
# url = f"https://fundf10.eastmoney.com/jjgg_{code}_3.html"

# page.get(url)
# page.wait.ele_displayed("#ggtable", timeout=10)
# table = page.ele("#ggtable")

# target_href = None
# kw = ["2026年第1季度报告", "二零二六年第1季度报告"]

# for a in table.eles("tag:a"):
#     t = re.sub(r"\s+", "", a.attr("title") or a.text)
#     if any(k in t for k in kw):
#         target_href = a.attr("href")
#         break

# print("匹配到季报链接：", target_href)

# if target_href:
#     page.get(target_href)

#     # ====================== 修复 1：等待文本真正加载完成 ======================
#     for _ in range(10):
#         pre = page.ele("#jjggzwcontentbody")
#         if pre and pre.text.strip():
#             break
#         time.sleep(0.5)
#     else:
#         print("正文一直空白，退出")
#         page.quit()
#         exit()

#     print("季报正文是否存在：", pre is not None)

#     full_text = pre.text
    
#     #切分1
#     start_idx = full_text.find("基金产品概况")
#     end_idx = full_text.find("投资目标", start_idx)  # 从start_idx开始查找，避免找到前面的
    
#     if start_idx == -1 or end_idx == -1:
#         print(f"未找到标记：start=基金产品概况, end=投资目标")
#     else:
#         target_text1 = full_text[start_idx:end_idx]
#     #切分2
#     start_idx2 = full_text.find("5.1 报告期末基金资产组合情况")
#     end_idx2 = full_text.find("5.6 报告期末", start_idx2)  # 从start_idx开始查找，避免找到前面的
    
#     if start_idx2 == -1 or end_idx2 == -1:
#         print(f"未找到标记：start=5.1 报告期末基金资产组合情况, end=5.6 报告期末按摊余成本占基金资产净值比例大小排名的前十名债券投资明细")
#     else:
#         target_text2 = full_text[start_idx2:end_idx2]
    
#     target_text=target_text1+target_text2
#     target_text=re.sub(r'\s+', ' ', target_text.strip())#换行符、制表符都换成空格
#     result = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', target_text)#去除中文之间的空格
#     print(result)


#     # ====================== 修复 2：把所有文本合成一段，无视分行 ======================
#     clean_text = re.sub(r'\s+', ' ', full_text.strip())
#     clean_text = re.sub(r'报\s*告\s*期\s*末\s*基\s*金\s*份\s*额\s*总\s*额', '报告期末基金份额总额', clean_text)#换行问题，”报告期末基 金份额总额 “中的空格可能出现在任意位置
#     print(clean_text)

#     data = {
#         "总资产-数值": "",
#         "净资产-数值": "",
#         "政策性金融债-比例": "",
#         "企业债券-比例": "",
#         "银行存款和结算备付金合计-比例": "",
#         "同业存单-比例": "",
#         "买入返售金融资产-比例": ""
#     }

#     # ====================== 修复 3：使用段落匹配，不依赖分行 ======================

#     # 1 净资产
#     pattern = re.compile(r'报告期末基金份额总额.*?([\d,]+\.\d+)')
#     res = pattern.search(clean_text)
#     if res:
#         data["净资产-数值"] = res.group(1)

#     # 2 总资产
#     pattern = re.compile(r'5.1 报告期末基金资产组合情况.*?5 合计.*?([\d,]+\.\d+)')
#     res = pattern.search(clean_text)
#     if res:
#         data["总资产-数值"] = res.group(1)

#     # 3 比例类（通用）
#     def get_ratio(keyword):
#         pattern = re.compile(fr'{keyword}.*?([\d,]+\.\d+)\s*([\d,]+\.\d+)')
#         res = pattern.search(clean_text)
#         if res and len(res.groups()) >= 2:
#             return res.group(2) + "%"
#         return ""

#     data["政策性金融债-比例"] = get_ratio("政策性金融债")
#     data["企业债券-比例"] = get_ratio("企业债券")
#     data["银行存款和结算备付金合计-比例"] = get_ratio("银行存款和结算备付金合计")
#     data["同业存单-比例"] = get_ratio("同业存单")
#     data["买入返售金融资产-比例"] = get_ratio("买入返售金融资产")

#     # 输出结果
#     print("\n===== 最终提取结果 =====")
#     for k, v in data.items():
#         print(f"{k}: {v}")

# page.quit()




# ====================== 【批量处理】 ======================
from DrissionPage import WebPage
import re
import time
import pandas as pd

# ====================== 【全局配置区｜后续改指标只修改此处】 ======================
# 1. 要匹配的季报标题关键词
# REPORT_KEYWORDS = ["2026年第1季度报告", "二零二六年第1季度报告","二0二六年第一号","二0二六年第1季度报告"]
year = input("请输入年份（如 2026）：")
quarter = input("请输入季度（如 1）：")

# 转换年份为中文数字
chinese_digits = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
year_chinese = "".join(chinese_digits[d] for d in year)

REPORT_KEYWORDS = [
    f"{year}年第{quarter}季度报告",
    f"二零{year_chinese[2:]}年第{quarter}季度报告",
    f"二0{year_chinese[2:]}年第一号",
    f"二0{year_chinese[2:]}年第{quarter}季度报告"
]

print(REPORT_KEYWORDS)

# 2. 纯数值指标：字典{输出列名: 页面匹配关键词}
NUM={
    "总资产-数值": "合计",
    "净资产-数值": "报告期末基金份额总额"
}
# 3. 比例类指标：字典{输出列名: 页面匹配关键词}
RATIO= {
    "政策性金融债-比例": "政策性金融债",
    "企业债券-比例": "企业债券",
    "银行存款和结算备付金合计-比例": "银行存款和结算备付金合计",
    "同业存单-比例": "同业存单",
    "买入返售金融资产-比例": "买入返售金融资产"
}
# 4.文件路径配置
INPUT_EXCEL = "fund_code.xlsx"    # 输入基金代码文件，A列须为【基金代码】
OUTPUT_EXCEL = f"{REPORT_KEYWORDS[0]}提取结果.xlsx"  # 输出结果文件，与"fund_code.xlsx"在同一文件夹
# ==============================================================================

# 初始化浏览器（只创建一次，循环复用）
page = WebPage()

# 读取输入Excel A列基金代码
df_input = pd.read_excel(INPUT_EXCEL,dtype=str)
code_list = df_input.iloc[:, 0].dropna().astype(str).tolist()  # A列去空转字符串
all_result = []  # 存储所有基金结果

# 循环遍历每一只基金代码
for fund_code in code_list:
    print(f"\n========== 正在处理基金：{fund_code} ==========")
    # 初始化该行数据字典，先填充空值
    row_data = {"基金代码": fund_code}
    # 合并两类指标的所有列名
    all_cols = list(NUM.keys()) + list(RATIO.keys())
    row_data.update({col: "" for col in all_cols})

    # 打开基金公告列表页
    url = f"https://fundf10.eastmoney.com/jjgg_{fund_code}_3.html"
    page.get(url)
    try:
        # 提取基金名称（修复多余后缀）
        page_title = page.title
        match = re.search(r'(.+?)\s*\(\d{6}\)', page_title)
        if match:
            fund_name = match.group(1).strip()
        else:
            fund_name = page_title
        row_data["基金名称"] = fund_name
        print(f"提取到基金名称：{fund_name}")

        page.wait.ele_displayed("#ggtable", timeout=10)
        table = page.ele("#ggtable")
    except Exception as e:
        print(f"{fund_code} 公告表格加载失败，跳过：{e}")
        all_result.append(row_data)
        continue

    # 匹配季报链接
    target_href = None
    for a in table.eles("tag:a"):
        title_raw = a.attr("title") or a.text
        clean_title = re.sub(r"\s+", "", title_raw)
        if any(k in clean_title for k in REPORT_KEYWORDS):
            target_href = a.attr("href")
            break
    if not target_href:
        print(f"{fund_code} 未匹配到目标季报，跳过")
        all_result.append(row_data)
        continue
    print("匹配到季报链接：", target_href)

    # 进入季报详情页
    page.get(target_href)
    # 循环等待正文文本加载完成
    pre = None
    for _ in range(10):
        temp_pre = page.ele("#jjggzwcontentbody")
        if temp_pre and temp_pre.text.strip():
            pre = temp_pre
            break
        time.sleep(0.5)
    if not pre:
        print(f"{fund_code} 季报正文空白，跳过")
        all_result.append(row_data)
        continue
    full_text = pre.text

    target_text1,target_text2,target_text3="","",""
    #切分1
    start_idx = full_text.find("基金产品概况")
    end_idx = full_text.find("投资目标", start_idx)  # 从start_idx开始查找，避免找到前面的
    if start_idx == -1 or end_idx == -1:
        print(f"未找到标记：start=基金产品概况, end=投资目标")
    else:
        target_text1 = full_text[start_idx:end_idx]
    #切分2
    start_idx2 = full_text.find("5.1 报告期末基金资产组合情况")
    end_idx2 = full_text.find("5.2 报告期债券回购融资情况", start_idx2)  # 从start_idx开始查找，避免找到前面的
    if start_idx2 == -1 or end_idx2 == -1:
        print(f"未找到标记：start=5.1 报告期末基金资产组合情况, end=5.2 报告期债券回购融资情况")
    else:
        target_text2 = full_text[start_idx2:end_idx2]
    #切分2
    start_idx3 = full_text.find("5.5 报告期末按债券品种分类的债券投资组合")
    end_idx3 = full_text.find("5.6 报告期末", start_idx2)  # 从start_idx开始查找，避免找到前面的
    if start_idx3 == -1 or end_idx3 == -1:
        print(f"未找到标记：start=5.5 报告期末按债券品种分类的债券投资组合, end=5.6 报告期末按摊余成本占基金资产净值比例大小排名的前十名债券投资明细")
    else:
        target_text3 = full_text[start_idx3:end_idx3]
    
    target_text=target_text1+target_text2+target_text3
    row_list=target_text.split("\n")
    res = [s for s in row_list if s and (s[-1].isdigit() or s[-1] == "-" or s[-1] == "－" or s[-1]=='份')]#数字or ”-“结尾
    print(res)

    # ====================== 【匹配指标｜后续改指标需修改此处】 ======================
    for item in res:
        if re.search(r'5\s+合计', item):#总资产,光找“合计”会误匹配至”10 合计“
            #print(f"yes,item:{item}")
            nums = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', item)
            if nums:
                print(nums[-2])
                row_data["总资产-数值"]=nums[-2] # 取倒数第二个最后一个数值（数值）
                continue
        else:
            # chinese_list = re.findall(r'[\u4e00-\u9fa5]', item)#筛选中文字符，但不一定出现在开头，弃用
            # cn=''.join(chinese_list)
            chinese = re.sub(r'^.*?([\u4e00-\u9fa5].*)', r'\1', item)#筛选中文字符并截取中文字符后的文本
            cn=chinese.split(" ")[0]
            if cn:
                if cn in "报告期末基金份额总额" or cn in '报告期末基金份额总额份' or cn in "报告期末基金份额份":#可能拆成2行了
                    nums = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', chinese)
                    if nums:
                        row_data["净资产-数值"]=nums[-1]  # 取最后一个数值（数值）
                        continue   
                for k,v in RATIO.items():
                    if v.startswith(cn.replace("其中：",'')):
                        print(f'v:{v},cn:{cn},chinese:{chinese}')
                        nums = re.findall(r'(?:\d+(?:,\d+)*(?:\.\d+)?)|-|－',chinese)
                        if nums:
                            row_data[k]=(str(nums[-1])+"%").replace("-%","-").replace("－%","－")  # 取最后一个数值（百分比）

    # 打印单只基金提取结果
    print("单基金提取结果：")
    for k, v in row_data.items():
        print(f"{k}: {v}")
    all_result.append(row_data)

# 全部基金处理完成，导出Excel（覆盖旧文件）
df_output = pd.DataFrame(all_result)
df_output.to_excel(OUTPUT_EXCEL, index=False)
print(f"\n===== 全部处理完成，结果已保存至 {OUTPUT_EXCEL} =====")

# 关闭浏览器
page.quit()
