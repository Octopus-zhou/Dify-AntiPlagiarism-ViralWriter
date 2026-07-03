import re

def main(draft_content: str, raw_viral_content: str) -> dict:
    """
    Dify 文本去重风控核心节点 (升级版: 自动多草稿并行筛选)
    输入: 
        draft_content: 包含分隔符的3篇AI重写草稿 (String)
        raw_viral_content: 最初输入的原始爆款文案 (String)
    """
    # 1. 对大模型产出的连续字符串进行高效正则切片，清洗掉空行
    drafts = [d.strip() for d in draft_content.split('===DRAFT_SPLIT===') if d.strip()]
    
    # 2. 预清洗原始文案：利用正则表达式剔除掉符号与空格，转化为字符级集合(Set)
    clean_pattern = re.compile(r'[^\u4e00-\u9fa5|a-zA-Z0-9]')
    str_raw = clean_pattern.sub('', raw_viral_content)
    set_raw = set(str_raw)
    
    # 鲁棒性防御：防止原始输入异常为空
    if not set_raw or not drafts:
        return {"best_similarity_score": 100.0, "is_safe": False, "best_draft": "", "msg": "输入文本数据异常为空"}
        
    best_score = 100.0  # 初始化一个极高查重值
    best_draft = ""
    
    # 3. 循环迭代，对 3 篇草稿进行并行的 Jaccard 相似度系数矩阵计算
    for draft in drafts:
        # 清洗单篇草稿内容
        str_draft = clean_pattern.sub('', draft)
        set_draft = set(str_draft)
        if not set_draft:
            continue
            
        # 计算交集与并集
        intersection_len = len(set_raw.intersection(set_draft))
        union_len = len(set_raw.union(set_draft))
        
        # 算出当前草稿的重合百分比
        current_score = (intersection_len / union_len) * 100
        
        # 【核心算法策略】：我们需要查重率最低（即原创度最高）的那篇
        if current_score < best_score:
            best_score = current_score
            best_draft = draft
            
    # 4. 根据自媒体大盘 15% 的去重红线进行最终布尔（Boolean）判定
    is_safe = best_score < 15.00
    
    return {
        "best_similarity_score": round(best_score, 2),
        "is_safe": is_safe,
        "best_draft": best_draft,
        "msg": "查重通过，已安全筛选最优原创文案" if is_safe else "全量草稿未过风控红线，触发反思流"
    }
