import pandas as pd
import re
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import numpy as np

# 确保已安装所需库: pip install pandas scikit-learn sentence-transformers torch
from sentence_transformers import SentenceTransformer

# --- 文件设置 ---
# 输入文件是上一步清理了翻译文本后的文件
input_filename = 'Google-Maps-Reviews_cleaned.csv'                  
# 输出文件将是最终可用于机器学习的纯数字特征文件
output_features_filename = 'Google-Maps-Reviews_features_engineered.csv'

try:
    # --- 1. 加载数据 ---
    df = pd.read_csv(input_filename, encoding='utf-8-sig')
    print("成功加载数据。原始数据形状:", df.shape)
    print("-" * 40)

    # --- 2. 布尔型特征处理 ---
    print("步骤 1/4: 处理布尔型特征...")
    df['isAdvertisement'] = df['isAdvertisement'].astype(bool).astype(int)
    df['isLocalGuide'] = df['isLocalGuide'].astype(bool).astype(int)
    print("完成。")
    print("-" * 40)

    # --- 3. 数值型特征处理 ---
    print("步骤 2/4: 处理数值型特征...")
    numeric_cols = ['reviewerNumberOfReviews', 'reviewsCount', 'stars', 'place_totalScore']
    imputer = SimpleImputer(strategy='median')
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    print("完成缺失值填充和标准化。")
    print("-" * 40)

    # --- 4. 分类特征处理 ---
    print("步骤 3/4: 处理分类特征 (One-Hot Encoding)...")
    categorical_cols = ['class_both', 'place_title']
    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_features = ohe.fit_transform(df[categorical_cols])
    new_col_names = ohe.get_feature_names_out(categorical_cols)
    encoded_df = pd.DataFrame(encoded_features, columns=new_col_names, index=df.index)
    df = pd.concat([df, encoded_df], axis=1)
    df.drop(columns=categorical_cols, inplace=True)
    print(f"完成。已生成 {encoded_df.shape[1]} 个新特征列。")
    print("-" * 40)
    
    # --- 5. 文本特征处理 ---
    print("步骤 4/4: 处理文本特征 (清洗与向量化)...")

    # 步骤 5.1: 文本清洗
    def clean_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'[^a-z0-9\s]', '', text) # 保留字母和数字
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # 清洗 'review_text' 列，并确保没有空值
    df['review_text_cleaned'] = df['review_text'].fillna('').apply(clean_text)
    print("文本清洗完成。")

    # 步骤 5.2: 使用Sentence-Transformer进行句子嵌入
    print("\n正在加载Sentence-Transformer模型... (首次运行需要下载模型，请稍候)")
    # 我们选用一个在性能和速度上表现都非常出色的通用模型
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 准备要编码的句子列表
    sentences_to_encode = df['review_text_cleaned'].tolist()
    
    print("\n正在生成句子向量... (这可能需要几分钟，取决于您的CPU性能)")
    # 使用模型进行编码，show_progress_bar=True 可以显示进度条
    sentence_embeddings = model.encode(sentences_to_encode, show_progress_bar=True)
    print("句子向量生成完毕！向量维度:", sentence_embeddings.shape)

    # 步骤 5.3: 将向量整合回DataFrame
    # 创建一个包含嵌入向量的新DataFrame
    embedding_cols = [f'embedding_{i}' for i in range(sentence_embeddings.shape[1])]
    embedding_df = pd.DataFrame(sentence_embeddings, columns=embedding_cols, index=df.index)
    
    # 将新编码的列与主DataFrame合并
    df = pd.concat([df, embedding_df], axis=1)
    print("已将文本向量合并到主数据框。")

    # --- 6. 最终清理和保存 ---
    # 删除原始文本列和清洗后的文本列，因为它们的信息已被向量捕获
    df.drop(columns=['review_text', 'review_text_cleaned', 'name'], inplace=True)
    print("\n已删除原始文本列，生成最终的纯数字特征矩阵。")

    # 保存最终的、可用于机器学习的特征文件
    df.to_csv(output_features_filename, index=False, encoding='utf-8-sig')
    print("-" * 40)
    print(f"🎉 所有预处理和特征工程完成！最终文件已保存为 '{output_features_filename}'。")
    print("最终数据形状:", df.shape)


except FileNotFoundError:
    print(f"错误：找不到文件 '{input_filename}'。请确保脚本和处理好的CSV文件在同一个文件夹下。")
except Exception as e:
    print(f"处理过程中发生未知错误：{e}")