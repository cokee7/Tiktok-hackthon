import tensorflow as tf
import numpy as np

import nltk
from nltk.tokenize import word_tokenize
from gensim.models import KeyedVectors
import matplotlib.pyplot as plt
import re
import warnings
warnings.filterwarnings("ignore")

from gensim.scripts.glove2word2vec import glove2word2vec
import os

# 利用预训练的向量模型glove 来进行
def load_glove_embeddings(glove_path, word2vec_output_path):
    """
    加载GloVe词向量并转换为gensim格式
    """
    # 如果还没有转换，先进行格式转换
    if not os.path.exists(word2vec_output_path):
        print("正在转换GloVe格式...")
        glove2word2vec(glove_input_file=glove_path,
                       word2vec_output_file=word2vec_output_path)

    # 加载转换后的词向量
    print("加载词向量...")
    glove_model = KeyedVectors.load_word2vec_format(word2vec_output_path,
                                                    binary=False,
                                                    encoding='utf-8')
    return glove_model

glove_path = 'D:/TikTok/src/embedding/glove.6B.300d.txt'
word2vec_output_path = 'D:/TikTok/src/embedding/glove.6B.300d.word2vec.txt'
glove_model = load_glove_embeddings(glove_path, word2vec_output_path)

embedding_dim = 300
print("Embedding dimension:", embedding_dim)


import pandas as pd
# 示例数据
data =pd.DataFrame({
    'comment': [
        'The coffee is amazing and the staff is friendly',
        'Great environment for studying with quiet atmosphere',
        'Plenty of parking spaces available',
        'The sushi was fresh and delicious',
        'Car repair service was excellent and affordable',
        'Beautiful garden with peaceful atmosphere',
        'Terrible wifi connection and slow service',
        'Amazing burger and crispy fries'
    ],
    'poi': [
        'Starbucks Coffee Shop',
        'Public Library',
        'Shopping Center Parking Lot',
        'Japanese Sushi Restaurant',
        'Auto Repair Mechanic',
        'Botanical Garden',
        'Coffee Shop',
        'Fast Food Restaurant'
    ],
    'relevance': [1, 1, 1, 1, 0, 1, 0, 0]  # 1=relevant, 0=irrelevant
})

print('Total samples:', len(data))

#构建训练数据
#训练文本
train_texts_orig = []
#训练目标
train_target = []

for index, row in data.iterrows():
    combined_text = row['comment'] + " [SEP] " + row['poi']
    train_texts_orig.append(combined_text)
    train_target.append(str(row['relevance']))

print("Training samples:", len(train_texts_orig))


# 英文预处理函数
def preprocess_english_text(text):
    """英文文本预处理"""
    text = text.lower()  # 转换为小写
    text = re.sub(r'[^\w\s]', ' ', text)  # 移除非字母数字字符
    text = re.sub(r'\s+', ' ', text)  # 移除多余空格
    return text.strip()


# 分词和tokenize
train_tokens = []
for text in train_texts_orig:
    # 预处理
    text = preprocess_english_text(text)

    # 使用nltk分词
    tokens = word_tokenize(text)

    processed_list = []
    for word in tokens:
        if word == '[sep]':  # 特殊分隔符
            processed_list.append(50001)
        else:
            try:
                # 在GloVe模型中查找词
                if word in glove_model:
                    idx = glove_model.key_to_index[word]  # gensim 4.0+ 用法
                    if idx < 50000:  # 只使用前50000个词
                        processed_list.append(idx)
                    else:
                        processed_list.append(0)
                else:
                    processed_list.append(0)  # 未知词
            except:
                processed_list.append(0)

    train_tokens.append(processed_list)

# 设置最大序列长度
num_tokens = [ len(tokens) for tokens in train_tokens ]
num_tokens = np.array(num_tokens)
print("len(train_tokens):", len(train_tokens))
print("len(num_tokens)", len(num_tokens))


# 平均tokens的长度
print("平均tokens的长度:", np.mean(num_tokens))


# 最长的评价tokens的长度
print("最长tokens的长度:",np.max(num_tokens))

# 取tokens平均值并加上两个tokens的标准差，
# 假设tokens长度的分布为正态分布，则max_tokens这个值可以涵盖95%左右的样本
max_tokens = np.mean(num_tokens) + 2 * np.std(num_tokens)
max_tokens = int(max_tokens)
print("max_tokens:", max_tokens)


# 取tokens的长度为220时，大约96%的样本被涵盖
# 我们对长度不足的进行padding，超长的进行修剪
np.sum(num_tokens < max_tokens) / len(num_tokens)

# 用来将tokens转换为文本
def reverse_tokens(tokens):
    text = ''
    for i in tokens:
        if i != 0:
            text = text + glove_model.index_to_key[i]+" "
        else:
            text = text + ' '
    return text

reverse = reverse_tokens(train_tokens[0])
print("reverse:", reverse)

# 准备建模
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, Embedding, LSTM, Bidirectional, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.optimizers import RMSprop, Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau


# 只使用前50000个词
num_words = 50000
# 初始化embedding_matrix，之后在keras上进行应用
embedding_matrix = np.zeros((num_words, embedding_dim))


# embedding_matrix为一个 [num_words，embedding_dim] 的矩阵
# 维度为 50000 * 300
for i in range(num_words):
    embedding_matrix[i, :] = glove_model[glove_model.index_to_key[i]]
embedding_matrix = embedding_matrix.astype('float32')

#检查一下输出是否对应 输出300则说明维度是对的
print(np.sum(glove_model[glove_model.index_to_key[30]] == embedding_matrix[30]))

# 进行padding和truncating， 输入的train_tokens是一个list
train_pad = pad_sequences(train_tokens, maxlen=max_tokens, padding='pre', truncating='pre')

# 准备target向量
train_target = np.array(train_target)
print("train_target:", train_target)


# 进行训练和测试样本的分割
from sklearn.model_selection import train_test_split

# 85%的样本用来训练，剩余15%用来测试
X_train, X_test, y_train, y_test = train_test_split(train_pad, train_target, test_size=0.15, random_state=1000)


# 用LSTM对样本进行分类
model = Sequential()
# 模型第一层为embedding
model.add(Embedding(num_words, embedding_dim, weights=[embedding_matrix], input_length=max_tokens, trainable=False))

model.add(Bidirectional(LSTM(units=64, return_sequences=True)))
model.add(Dropout(0.1))

model.add(LSTM(units=16, return_sequences=False))
model.add(Dropout(0.1))

model.add(Dense(1, activation='sigmoid'))

# 我们使用adam以0.001的learning rate进行优化
optimizer = Adam(learning_rate=1e-3)
model.compile(loss='binary_crossentropy', optimizer=optimizer,  metrics=['accuracy'])


# 查看模型的结构
model.summary()


