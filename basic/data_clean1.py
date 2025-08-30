import pandas as pd

# --- 文件设置 ---
input_filename = 'Google-Maps-Reviews_filter.csv'
output_filename = 'Google-Maps-Reviews_processed.csv'

try:
    # 1. 读取CSV文件，并使用 encoding='utf-8-sig' 来自动处理BOM字符
    # 这是解决这个问题的关键
    df = pd.read_csv(input_filename, encoding='utf-8-sig')
    print(f"成功读取文件 '{input_filename}'，共 {len(df)} 行数据。")

    # 清理所有列名可能存在的首尾空格，作为双重保险
    df.columns = df.columns.str.strip()

    # 2. 创建筛选条件：只选中'translatedLanguage'列【不为空】的行
    #    这个条件确保我们只会处理那些有翻译文本的行
    condition = df['translatedLanguage'].notna()
    
    rows_to_update = condition.sum()
    print(f"找到 {rows_to_update} 行需要进行替换操作。")

    # 3. 执行精确替换：
    #    只有满足条件的行(即translatedLanguage不为空的行)才会被修改
    #    其他行将保持原样
    df.loc[condition, 'review_text'] = df.loc[condition, 'textTranslated']
    
    print("替换操作完成。")

    # 4. 删除不再需要的列
    df.drop(columns=['textTranslated', 'translatedLanguage'], inplace=True)
    print("已删除 'textTranslated' 和 'translatedLanguage' 列。")

    # 5. 将处理后的DataFrame保存到新的CSV文件
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n处理成功！结果已保存到新文件 '{output_filename}'。")

except FileNotFoundError:
    print(f"错误：找不到文件 '{input_filename}'。请确保脚本和CSV文件在同一个文件夹下。")
except KeyError as e:
     print(f"发生列名错误：{e}。请再次运行诊断脚本，并把完整的列名复制给我。")
except Exception as e:
    print(f"处理过程中发生未知错误：{e}")