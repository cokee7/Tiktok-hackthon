import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import joblib
from gensim.models import Word2Vec

# --- 1. 加载所有保存好的构件 ---
@st.cache_resource
def load_artifacts():
    artifact_dir = "model_artifacts"
    try:
        median_values = joblib.load(os.path.join(artifact_dir, 'median_values.pkl'))
        capping_limits = joblib.load(os.path.join(artifact_dir, 'capping_limits.pkl'))
        scaler = joblib.load(os.path.join(artifact_dir, 'scaler.pkl'))
        w2v_model = Word2Vec.load(os.path.join(artifact_dir, "word2vec.model"))
        final_model = joblib.load(os.path.join(artifact_dir, 'best_multilabel_model.pkl'))
        final_feature_order = joblib.load(os.path.join(artifact_dir, 'final_feature_order.pkl'))
        
        all_cols_from_training = joblib.load(os.path.join(artifact_dir, 'feature_columns.pkl'))
        place_title_options = sorted([col.replace('place_title_', '') for col in all_cols_from_training if col.startswith('place_title_')])
        class_both_options = sorted([col.replace('class_both_', '') for col in all_cols_from_training if col.startswith('class_both_')])
        
        return median_values, capping_limits, scaler, w2v_model, final_model, final_feature_order, place_title_options, class_both_options
    except Exception as e:
        st.error(f"加载模型文件时出错: {e}")
        st.error(f"请确保 '{artifact_dir}' 文件夹存在，并且包含了所有必要的 .pkl, .model 文件。")
        return [None] * 8

# 加载模型和工具
median_values, capping_limits, scaler, w2v_model, final_model, final_feature_order, place_title_options, class_both_options = load_artifacts()

# --- 2. 定义完整的预处理函数 ---
def preprocess_input(user_input):
    df = pd.DataFrame([user_input])

    numeric_cols = ['reviewerNumberOfReviews', 'reviewsCount', 'stars', 'place_totalScore']
    outlier_cols = ['reviewerNumberOfReviews', 'reviewsCount']
    df[numeric_cols] = df[numeric_cols].fillna(pd.Series(median_values))
    for col in outlier_cols:
        df.loc[df[col] > capping_limits[col], col] = capping_limits[col]
    df[numeric_cols] = scaler.transform(df[numeric_cols])

    df['isLocalGuide'] = df['isLocalGuide'].astype(int)
    
    def preprocess_text_for_w2v(text):
        if not isinstance(text, str): return []
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        return text.split()
    
    def get_sentence_vector(tokens, model):
        vectors = [model.wv[word] for word in tokens if word in model.wv]
        if len(vectors) == 0: return np.zeros(model.vector_size)
        return np.mean(vectors, axis=0)

    tokens = preprocess_text_for_w2v(df['review_text'].iloc[0])
    sentence_vector = get_sentence_vector(tokens, w2v_model)
    w2v_df = pd.DataFrame([sentence_vector], columns=[f'w2v_{i}' for i in range(100)])

    df_processed = df.drop(columns=['class_both', 'place_title', 'review_text'])
    df_processed = pd.concat([df_processed, w2v_df], axis=1)

    final_input_df = pd.DataFrame(columns=final_feature_order)
    final_input_df = pd.concat([final_input_df, df_processed], axis=0).fillna(0)

    class_col_name_cleaned = 'class_both_' + re.sub(r'[^A-Za-z0-9_]+', '_', user_input['class_both'])
    if class_col_name_cleaned in final_input_df.columns:
        final_input_df[class_col_name_cleaned] = 1
        
    place_col_name_cleaned = 'place_title_' + re.sub(r'[^A-Za-z0-9_]+', '_', user_input['place_title'])
    if place_col_name_cleaned in final_input_df.columns:
        final_input_df[place_col_name_cleaned] = 1
        
    return final_input_df[final_feature_order]

# --- 3. Streamlit 网页界面 ---
st.set_page_config(page_title="违规评论检测器", page_icon="🚨", layout="wide")
st.title("🚨 Google Maps 违规评论智能检测器 (Demo)")
st.markdown("输入评论及相关信息，后台将调用训练好的 **LightGBM** 模型进行实时检测。")

if final_model:
    # --- ✨ 关键修正：定义决策阈值 ---
    # 为了追求高召回率，我们将阈值设为0.3
    THRESHOLDS = {
        'if_ad': 0.3,
        'if_irrelevant': 0.3,
        'if_not_experience': 0.3
    }
    st.info(f"当前检测策略：高召回率模式（阈值 = {list(THRESHOLDS.values())[0]}）。任何违规可能性超过此值的评论都将被标记为违规。")
    st.markdown("---")

    # 创建输入界面
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 评论内容")
        review_text_input = st.text_area("Review Text", "I didn't came here before but it sounds good!", height=150)
        stars_input = st.slider("星级 (Stars)", 1, 5, 2)
        is_local_guide_input = st.checkbox("是本地向导 (Is Local Guide)?", False)

    with col2:
        st.subheader("👤 评论者与地点信息")
        reviewer_reviews_input = st.number_input("评论者历史评论数", min_value=0, value=1)
        place_reviews_input = st.number_input("地点总评论数", min_value=0, value=50)
        place_score_input = st.slider("地点总评分", 1.0, 5.0, 3.5, 0.1)
        place_title_input = st.selectbox("地点名称", options=place_title_options, index=0 if not place_title_options else min(5, len(place_title_options)-1))
        class_both_input = st.selectbox("地点类别", options=class_both_options, index=0 if not class_both_options else min(5, len(class_both_options)-1))

    if st.button("开始检测", type="primary", use_container_width=True):
        if not review_text_input:
            st.warning("请输入评论内容以进行检测！")
        else:
            user_input_data = {
                'isLocalGuide': is_local_guide_input,
                'reviewerNumberOfReviews': reviewer_reviews_input,
                'reviewsCount': place_reviews_input,
                'stars': stars_input,
                'review_text': review_text_input,
                'place_title': place_title_input,
                'place_totalScore': place_score_input,
                'class_both': class_both_input
            }
            
            with st.spinner("模型正在分析中，请稍候..."):
                features = preprocess_input(user_input_data)
                prediction_proba = final_model.predict_proba(features)

            st.subheader("🔍 检测结果")
            label_columns = ['if_ad', 'if_irrelevant', 'if_not_experience']
            results_cols = st.columns(len(label_columns))
            violation_found_count = 0
            
            for i, label in enumerate(label_columns):
                with results_cols[i]:
                    prob = prediction_proba[i][0, 1]
                    threshold = THRESHOLDS.get(label, 0.5) # 使用我们定义的阈值
                    
                    if prob >= threshold:
                        violation_found_count += 1
                        st.metric(label=label, value="检测到违规", delta=f"{prob:.1%} 可能性", delta_color="inverse")
                    else:
                        st.metric(label=label, value="合规", delta=f"{prob:.1%} 可能性", delta_color="off")

            st.markdown("---")
            if violation_found_count > 0:
                st.warning(f"**综合结论：** 该评论检测到 **{violation_found_count}** 项潜在违规，建议进行人工审核。")
            else:
                st.balloons()
                st.success("**综合结论：** 🎉 评论内容合规。")
else:
    st.error("模型加载失败，请先运行 `train_and_save_artifacts.py`。")