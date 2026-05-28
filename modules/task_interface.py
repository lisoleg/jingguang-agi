"""
task_interface.py - 多任务处理接口（增强版）

基于复合体理学共识实在论，建立主客观统一的认知基准：
- 文本理解：解析输入文本，提取语义信息
- 简单推理：基于规则进行逻辑推理
- 决策制定：综合信息做出决策
- 任务调度：管理多任务并发处理

核心功能（增强版）：
1. 文本处理接口：理解、分析、生成文本（扩展词库）
2. 推理接口：因果推理、类比推理、演绎推理、归纳推理（新增规则）
3. 决策接口：基于多维度评估做决策
4. 任务管理：任务注册、执行、监控
5. 向量知识库：存储和检索知识
6. 神经网络接口：替代部分规则引擎
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import time
import math
import json
import sys
import os

try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    Word2Vec = None
    GENSIM_AVAILABLE = False

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

from modules.agi_core import LayerType
from modules.neural_network import NeuralNetwork


class TaskType(Enum):
    """任务类型"""
    TEXT_UNDERSTANDING = "text"       # 文本理解
    SIMPLE_REASONING = "reasoning"    # 简单推理
    DECISION_MAKING = "decision"      # 决策制定
    PATTERN_MATCH = "pattern"         # 模式匹配
    NEURAL_PROCESS = "neural"         # 神经网络处理
    GENERAL = "general"               # 通用任务


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务定义"""
    
    id: str
    type: TaskType
    input_data: Any
    expected_output: Any = None
    status: TaskStatus = TaskStatus.PENDING
    output: Any = None
    confidence: float = 0.0  # 输出置信度
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"Task(id={self.id}, type={self.type.value}, status={self.status.value})"


class TextProcessor:
    """文本处理器 - 处理文本理解相关任务（扩展版）
    
    使用轻量级神经网络替代部分规则引擎：
    - 情感分析使用神经网络（3分类：positive/negative/neutral）
    - 概念识别暂时保留规则方法（基于concept_map查找）
    """
    
    def __init__(self):
        # Word2Vec configuration
        self.use_word2vec = False
        self.word2vec_model = None
        self.word2vec_vector_size = 50  # 50维向量，平衡性能和效果
        self.gensim_available = GENSIM_AVAILABLE
        
        # 词汇表大小（用于哈希方法回退）
        self.vocab_size = 768
        
        # 初始化神经网络（根据Word2Vec可用性调整输入维度）
        nn_model_path = "sentiment_nn.json"
        
        # 尝试加载已训练的神经网络
        try:
            if self.gensim_available:
                self._init_word2vec()
                if self.use_word2vec:
                    self.sentiment_net = NeuralNetwork(
                        layer_sizes=[self.word2vec_vector_size, 64, 3],
                        activations=["relu", "softmax"]
                    )
                else:
                    self.sentiment_net = NeuralNetwork(
                        layer_sizes=[self.vocab_size, 64, 3],
                        activations=["relu", "softmax"]
                    )
            else:
                self.sentiment_net = NeuralNetwork(
                    layer_sizes=[self.vocab_size, 64, 3],
                    activations=["relu", "softmax"]
                )
            
            # 尝试加载模型权重
            if os.path.exists(nn_model_path):
                if self.sentiment_net.load_model(nn_model_path):
                    print(f"✅ 从文件加载神经网络模型")
                else:
                    raise Exception("加载模型失败")
            else:
                raise Exception("模型文件不存在")
                    
        except Exception as e:
            print(f"⚠️ 加载神经网络模型失败: {e}，重新训练...")
            # 训练新模型
            self._train_sentiment_network()
            # 保存模型
            self.sentiment_net.save_model(nn_model_path)
            print(f"✅ 神经网络模型已保存到 {nn_model_path}")
        
        # 扩展后的关键词-概念映射（新增AGI相关、技术、情感等）
        self.concept_map = {
            # 基础社交
            "你好": "greeting",
            "hello": "greeting",
            "hi": "greeting",
            "再见": "farewell",
            "bye": "farewell",
            "谢谢": "gratitude",
            "thanks": "gratitude",
            "帮助": "help_request",
            "help": "help_request",
            "问题": "question",
            "question": "question",
            "错误": "error",
            "error": "error",
            "成功": "success",
            "success": "success",
            
            # AGI相关概念
            "智能": "intelligence",
            "人工智能": "ai",
            "ai": "ai",
            "agi": "agi",
            "通用人工智能": "agi",
            "学习": "learning",
            "learning": "learning",
            "推理": "reasoning",
            "reasoning": "reasoning",
            "决策": "decision",
            "decision": "decision",
            "复合体": "complex",
            "complex": "complex",
            "能量": "energy",
            "energy": "energy",
            "认知": "cognition",
            "cognition": "cognition",
            "感知": "perception",
            "perception": "perception",
            "行动": "action",
            "action": "action",
            
            # 技术术语
            "神经网络": "neural_network",
            "neural": "neural_network",
            "network": "neural_network",
            "向量": "vector",
            "vector": "vector",
            "数据库": "database",
            "database": "database",
            "算法": "algorithm",
            "algorithm": "algorithm",
            "模型": "model",
            "model": "model",
            "训练": "training",
            "training": "training",
            "数据": "data",
            "data": "data",
            
            # 情感扩展
            "喜欢": "like",
            "love": "like",
            "讨厌": "dislike",
            "hate": "dislike",
            "希望": "hope",
            "hope": "hope",
            "害怕": "fear",
            "fear": "fear",
            "期待": "expectation",
            "expect": "expectation",
        }
        
        # 扩展后的情感词库
        self.sentiment_words = {
            "positive": [
                "好", "棒", "优秀", "喜欢", "爱", "高兴", "开心", "满意", "happy", "good", "great",
                "完美", "精彩", "赞", "牛", "厉害", "强大", "excellent", "wonderful", "amazing",
                "成功", "顺利", "进步", "提升", "优化", "改进", "success", "successful", "improved"
            ],
            "negative": [
                "坏", "差", "讨厌", "恨", "难过", "伤心", "失望", "bad", "terrible", "sad",
                "失败", "错误", "问题", "bug", "崩溃", "error", "fail", "failed", "wrong",
                "糟糕", "难受", "痛苦", "烦恼", "awful", "painful", "trouble"
            ],
            "neutral": [
                "一般", "还行", "差不多", "ok", "okay", "average", "medium", "normal"
            ]
        }
        
        # 意图关键词
        self.intent_keywords = {
            "question": ["?", "？", "什么", "怎么", "why", "what", "how", "when", "where"],
            "request": ["请", "please", "帮", "希望", "可以", "能不能", "can", "could", "would"],
            "exclamation": ["!", "！", "太", "真", "非常", "特别", "extremely", "very", "so"],
            "statement": []  # 默认
        }
        
        # 训练神经网络（情感分析）
        # 已在上方逻辑中完成（加载或训练）
    
    def _init_word2vec(self):
        """初始化Word2Vec模型，使用training_data.json训练（支持持久化）"""
        model_path = "word2vec.model"
        
        # 尝试加载已有模型
        if GENSIM_AVAILABLE and os.path.exists(model_path):
            try:
                self.word2vec_model = Word2Vec.load(model_path)
                self.use_word2vec = True
                print("✅ 从文件加载Word2Vec模型")
                return
            except Exception as e:
                print(f"加载Word2Vec模型失败: {e}，重新训练...")
        
        try:
            # 加载训练数据
            with open('training_data.json', 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # 准备Word2Vec训练语料（分词）
            sentences = []
            for item in training_data:
                text = item['text']
                tokens = self._tokenize(text)
                if tokens:
                    sentences.append(tokens)
            
            if len(sentences) < 1:
                raise ValueError("无有效语料训练Word2Vec")
            
            # 训练Word2Vec模型（小规模，CBOW算法）
            self.word2vec_model = Word2Vec(
                sentences=sentences,
                vector_size=self.word2vec_vector_size,
                window=5,
                min_count=1,
                sg=0,  # CBOW（小数据更快）
                workers=1
            )
            self.use_word2vec = True
            print(f"✅ Word2Vec模型训练完成，向量维度：{self.word2vec_vector_size}")
            
            # 保存模型
            if GENSIM_AVAILABLE:
                self.word2vec_model.save(model_path)
                print(f"✅ Word2Vec模型已保存到 {model_path}")
            
        except FileNotFoundError:
            print("⚠️ 未找到training_data.json，Word2Vec初始化失败")
            self.use_word2vec = False
        except Exception as e:
            print(f"⚠️ Word2Vec训练失败: {str(e)}")
            self.use_word2vec = False
    
    def _tokenize(self, text: str) -> List[str]:
        """分词方法：优先使用jieba优化中文分词，回退到简单分词"""
        # 使用jieba分词（如果可用）
        if HAS_JIEBA:
            try:
                return list(jieba.lcut(text))
            except:
                pass  # 回退到简单分词
        
        # 简单分词：中文按字拆分，英文按空格拆分
        import re
        tokens = []
        # 匹配中文字符和非中文字符段
        for part in re.findall(r'[\u4e00-\u9fff]|[^\u4e00-\u9fff\s]+', text):
            if re.match(r'[\u4e00-\u9fff]', part):
                # 中文：按字符拆分
                tokens.extend(list(part))
            else:
                # 非中文：按空格拆分并转为小写
                tokens.extend(part.lower().split())
        return tokens

    def _text_to_vector(self, text: str) -> List[float]:
        """将文本转换为向量（支持Word2Vec或哈希方法）
        
        Args:
            text: 输入文本
            
        Returns:
            Word2Vec向量（50维）或哈希向量（768维）
        """
        # 使用Word2Vec生成向量
        if self.use_word2vec and self.word2vec_model:
            tokens = self._tokenize(text)
            word_vectors = []
            for token in tokens:
                if token in self.word2vec_model.wv:
                    word_vectors.append(self.word2vec_model.wv[token])
            if word_vectors:
                # 平均词向量得到文本向量
                avg_vector = [sum(dim) / len(word_vectors) for dim in zip(*word_vectors)]
                return avg_vector
            else:
                return [0.0] * self.word2vec_vector_size
        # 回退到哈希方法
        else:
            vector = [0.0] * self.vocab_size
            
            if not text:
                return vector
            
            words = text.lower().split()
            for word in words:
                # 使用哈希函数将词映射到词汇表索引
                idx = hash(word) % self.vocab_size
                vector[idx] += 1.0
            
            # 归一化
            max_val = max(vector)
            if max_val > 0:
                vector = [v / max_val for v in vector]
            
            return vector
    
    def _train_sentiment_network(self):
        """训练情感分析神经网络
        
        优先使用training_data.json，失败则回退到sentiment_words
        3分类：positive(0), negative(1), neutral(2)
        """
        training_data = []
        
        # 优先从training_data.json加载训练数据
        try:
            with open('training_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                text = item['text']
                sentiment = item['sentiment']
                vector = self._text_to_vector(text)
                
                # 创建目标输出（one-hot）
                target = [0.0, 0.0, 0.0]
                if sentiment == 'positive':
                    target[0] = 1.0
                elif sentiment == 'negative':
                    target[1] = 1.0
                else:  # neutral
                    target[2] = 1.0
                
                training_data.append((vector, target))
            print(f"从training_data.json加载了{len(training_data)}条训练数据")
            
        except FileNotFoundError:
            print("未找到training_data.json，使用sentiment_words训练")
            self._load_training_from_sentiment_words(training_data)
        except Exception as e:
            print(f"加载训练数据失败: {str(e)}，使用sentiment_words训练")
            self._load_training_from_sentiment_words(training_data)
        
        # 训练神经网络（根据方法调整轮次）
        if training_data:
            # Word2Vec使用更多训练轮次，哈希方法使用较少轮次
            epochs = 50 if self.use_word2vec else 20
            self.sentiment_net.train(training_data, epochs=epochs, learning_rate=0.3, verbose=False)
            print(f"情感网络训练完成，轮次：{epochs}，数据量：{len(training_data)}")
    
    def _load_training_from_sentiment_words(self, training_data: List):
        """从sentiment_words加载训练数据（回退方法）"""
        for sent_type, words in self.sentiment_words.items():
            for word in words:
                vector = self._text_to_vector(word)
                target = [0.0, 0.0, 0.0]
                if sent_type == "positive":
                    target[0] = 1.0
                elif sent_type == "negative":
                    target[1] = 1.0
                else:
                    target[2] = 1.0
                training_data.append((vector, target))
    
    def _rule_based_sentiment(self, text_lower: str) -> str:
        """基于规则的情感分析（回退方案）
        
        Args:
            text_lower: 小写的文本
            
        Returns:
            情感类型：positive/negative/neutral
        """
        sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for sent_type, words in self.sentiment_words.items():
            for w in words:
                if w in text_lower:
                    sentiment_scores[sent_type] += 1
        
        if sentiment_scores["positive"] > sentiment_scores["negative"]:
            return "positive"
        elif sentiment_scores["negative"] > sentiment_scores["positive"]:
            return "negative"
        else:
            return "neutral"
    
    def understand(self, text: str) -> Dict[str, Any]:
        """理解文本内容，返回语义分析结果
        
        使用神经网络进行情感分析，规则引擎进行概念识别
        当神经网络置信度低时，回退到规则方法
        """
        if not text:
            return {"meaning": "empty", "confidence": 0.0}
        
        text_lower = text.lower()
        concepts = []
        confidence = 0.5
        
        # 概念识别（使用规则：从concept_map中查找）
        for keyword, concept in self.concept_map.items():
            if keyword in text_lower:
                if concept not in concepts:  # 避免重复
                    concepts.append(concept)
                    confidence += 0.05
        
        # 情感分析（混合策略：规则+神经网络）
        # 先检查文本中是否包含明确的情感词
        rule_sentiment = self._rule_based_sentiment(text_lower)
        
        # 如果规则方法找到明确的情感（不是neutral），直接使用
        if rule_sentiment != "neutral":
            sentiment = rule_sentiment
            sentiment_outputs = [0.0, 0.0, 0.0]
            if sentiment == "positive":
                sentiment_outputs[0] = 1.0
            elif sentiment == "negative":
                sentiment_outputs[1] = 1.0
            # 根据情感调整置信度
            confidence += 0.15
        else:
            # 否则使用神经网络预测
            vector = self._text_to_vector(text)
            sentiment_outputs = self.sentiment_net.predict(vector)
            
            # 解析神经网络输出
            sentiment_idx = sentiment_outputs.index(max(sentiment_outputs))
            sentiment = ["positive", "negative", "neutral"][sentiment_idx]
            
            # 根据情感调整置信度
            if sentiment == "positive" or sentiment == "negative":
                confidence += 0.15
            else:
                confidence += 0.05
        
        # 构建情感分数字典
        sentiment_scores = {
            "positive": sentiment_outputs[0],
            "negative": sentiment_outputs[1],
            "neutral": sentiment_outputs[2]
        }
        
        # 意图识别（使用规则）
        intent = "statement"  # 默认陈述
        for intent_type, keywords in self.intent_keywords.items():
            if any(kw in text_lower for kw in keywords):
                intent = intent_type
                break
        
        # 计算文本复杂度（简单指标）
        word_count = len(text.split())
        complexity = "simple" if word_count < 10 else "medium" if word_count < 30 else "complex"
        
        return {
            "meaning": concepts[0] if concepts else "general_text",
            "concepts": concepts,
            "sentiment": sentiment,
            "sentiment_scores": sentiment_scores,
            "intent": intent,
            "confidence": min(1.0, confidence),
            "length": len(text),
            "word_count": word_count,
            "complexity": complexity
        }
    
    def process(self, text: str) -> Dict[str, Any]:
        """处理文本 - 接口方法（使用神经网络）
        
        Args:
            text: 输入文本
            
        Returns:
            包含文本理解结果的字典，包括：
            - concepts: 识别出的概念列表
            - sentiment: 情感（positive/negative/neutral）
            - confidence: 置信度
            - 其他字段（intent, length, word_count, complexity等）
        """
        return self.understand(text)
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """提取关键词（增强版：基于词频+概念权重）"""
        if not text:
            return []
        
        # 简单分词（按空格和标点）
        words = re.findall(r'\w+', text.lower())
        
        # 停用词（扩展）
        stopwords = {
            "的", "了", "是", "在", "有", "和", "a", "the", "is", "are", "in", "on", "at", "to", "and",
            "我", "你", "他", "她", "它", "我们", "你们", "他们", "i", "you", "he", "she", "it", "we", "they"
        }
        words = [w for w in words if w not in stopwords and len(w) > 1]
        
        # 统计词频
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        
        # 概念词加权
        for w in words:
            if w in self.concept_map:
                freq[w] = freq.get(w, 0) + 2  # 概念词权重更高
        
        # 排序返回
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:max_keywords]]
    
    def generate_response(self, understanding: Dict[str, Any]) -> str:
        """根据理解结果生成简单回复（增强版）"""
        meaning = understanding.get("meaning", "general_text")
        sentiment = understanding.get("sentiment", "neutral")
        intent = understanding.get("intent", "statement")
        concepts = understanding.get("concepts", [])
        
        responses = {
            "greeting": "你好！我是AGI原型系统，可以帮您处理文本、推理和决策任务。",
            "farewell": "再见！期待下次交流。",
            "gratitude": "不客气，很高兴能帮助您。",
            "help_request": "我可以帮助您处理文本理解、推理分析和决策制定等任务。",
            "question": "这是一个很好的问题，让我思考一下。",
            "error": "检测到错误，请检查输入。",
            "success": "任务完成成功！",
            "general_text": "我已收到您的输入，正在处理中。",
            # AGI相关
            "agi": "通用人工智能（AGI）是我正在学习的核心概念。",
            "ai": "人工智能是一个广阔的领域，我正在努力变得更智能。",
            "learning": "学习是智能的核心，我也在不断学习和进步。",
            "complex": "复合体结构让我能够分层处理信息。",
            "energy": "能量管理帮助我优化资源分配。",
        }
        
        base_response = responses.get(meaning, responses["general_text"])
        
        # 根据情感调整
        if sentiment == "positive" and intent != "question":
            base_response += " 很高兴听到您这么说！"
        elif sentiment == "negative":
            base_response += " 如果需要帮助，请告诉我。"
        
        # 根据概念添加额外信息
        if "agi" in concepts or "ai" in concepts:
            base_response += " 我基于复合体理学框架构建。"
        
        return base_response


class ReasoningEngine:
    """推理引擎 - 处理简单推理任务（增强版：新增多种推理规则）"""
    
    def __init__(self):
        # 事实库
        self.facts: Dict[str, Any] = {}
        # 规则库（增强：支持多种推理类型）
        self.rules: List[Tuple[str, Callable, Callable]] = []  # (name, condition, conclusion)
        # 知识库（简单表示）
        self.knowledge_base: List[Dict] = []
    
    def add_fact(self, key: str, value: Any) -> None:
        """添加事实"""
        self.facts[key] = value
    
    def add_rule(self, name: str, condition: Callable[[Dict], bool], 
                 conclusion: Callable[[Dict], Any]) -> None:
        """添加推理规则"""
        self.rules.append((name, condition, conclusion))
    
    def add_knowledge(self, knowledge: Dict) -> None:
        """添加知识到知识库"""
        self.knowledge_base.append(knowledge)
    
    def reason(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """执行推理，返回推理结果（增强版）"""
        context = context or {}
        all_facts = {**self.facts, **context}
        
        # 多种推理方式
        conclusions = []
        confidence = 0.0
        
        # 1. 规则推理：检查规则
        for name, condition, conclusion in self.rules:
            try:
                if condition(all_facts):
                    result = conclusion(all_facts)
                    conclusions.append({
                        "type": "rule_based",
                        "rule": name,
                        "result": result,
                        "confidence": 0.7
                    })
                    confidence = max(confidence, 0.7)
            except:
                pass  # 规则执行失败，跳过
        
        # 2. 因果关系推理（增强版）
        if "因为" in query or "because" in query.lower():
            parts = query.split("因为") if "因为" in query else query.split("because")
            if len(parts) > 1:
                cause = parts[1].strip()
                # 更精细的因果推理
                effect = self._infer_effect(cause)
                conclusions.append({
                    "type": "causal",
                    "cause": cause,
                    "effect": effect,
                    "inference": f"如果{cause}，则{effect}",
                    "confidence": 0.6
                })
                confidence = max(confidence, 0.6)
        
        # 3. 类比推理（增强版）
        if any(kw in query.lower() for kw in ["像", "类比", "similar", "analogy"]):
            analogy = self._find_analogy(query)
            conclusions.append({
                "type": "analogy",
                "analogy": analogy,
                "inference": f"基于类比推理：{analogy}",
                "confidence": 0.5
            })
            confidence = max(confidence, 0.5)
        
        # 4. 演绎推理（新增）：从一般到特殊
        if any(kw in query.lower() for kw in ["所有", "都", "always", "all"]):
            deduction = self._deductive_reasoning(query, all_facts)
            if deduction:
                conclusions.append(deduction)
                confidence = max(confidence, 0.65)
        
        # 5. 归纳推理（新增）：从特殊到一般
        if len(self.knowledge_base) > 3:
            induction = self._inductive_reasoning(query)
            if induction:
                conclusions.append(induction)
                confidence = max(confidence, 0.55)
        
        return {
            "query": query,
            "conclusions": conclusions,
            "confidence": confidence if conclusions else 0.3,
            "facts_used": list(all_facts.keys())[:5],
            "reasoning_types": list(set(c["type"] for c in conclusions))
        }
    
    def _infer_effect(self, cause: str) -> str:
        """根据原因推断可能的结果"""
        cause_lower = cause.lower()
        
        # 简单的因果映射
        if "能量高" in cause_lower or "energy high" in cause_lower:
            return "系统适合处理复杂任务"
        elif "能量低" in cause_lower or "energy low" in cause_lower:
            return "系统应优先处理重要任务"
        elif "错误" in cause_lower or "error" in cause_lower:
            return "需要检查并修复问题"
        elif "学习" in cause_lower or "learning" in cause_lower:
            return "系统能力将得到提升"
        else:
            return "可能发生相应结果"
    
    def _find_analogy(self, query: str) -> str:
        """查找类比关系"""
        query_lower = query.lower()
        
        if "神经网络" in query_lower or "neural" in query_lower:
            return "神经网络类似于人脑的神经元网络"
        elif "学习" in query_lower or "learning" in query_lower:
            return "学习过程类似于生物体的适应过程"
        elif "能量" in query_lower or "energy" in query_lower:
            return "能量管理类似于生物体的新陈代谢"
        else:
            return "基于已知模式进行类比推理"
    
    def _deductive_reasoning(self, query: str, facts: Dict) -> Optional[Dict]:
        """演绎推理：从一般规则推导特殊结论"""
        # 简单演绎：如果所有A都是B，x是A，则x是B
        if "所有" in query and "都" in query:
            return {
                "type": "deduction",
                "pattern": "所有A都是B，x是A，所以x是B",
                "inference": "基于演绎推理得出结论",
                "confidence": 0.65
            }
        return None
    
    def _inductive_reasoning(self, query: str) -> Optional[Dict]:
        """归纳推理：从特殊案例总结一般规律"""
        if len(self.knowledge_base) < 3:
            return None
        
        # 简单归纳：统计知识库中的模式
        return {
            "type": "induction",
            "pattern": "基于多个案例总结规律",
            "sample_size": len(self.knowledge_base),
            "inference": "归纳得出结论：观察多个案例后发现规律",
            "confidence": 0.55
        }
    
    def clear(self) -> None:
        """清空事实和规则"""
        self.facts.clear()
        self.rules.clear()
        self.knowledge_base.clear()


class DecisionMaker:
    """决策制定器 - 综合信息做出决策（增强版）"""
    
    def __init__(self):
        self.criteria_weights: Dict[str, float] = {}
    
    def decide(self, options: List[Dict], context: Dict = None) -> Dict[str, Any]:
        """从多个选项中做出决策（增强版：支持多维度评分）"""
        if not options:
            return {"choice": None, "confidence": 0.0, "reason": "无选项可供选择"}
        
        if len(options) == 1:
            return {
                "choice": options[0],
                "confidence": 0.8,
                "reason": "唯一选项，直接选择"
            }
        
        # 多维度评分
        scores = []
        for i, option in enumerate(options):
            score = 0.0
            count = 0
            details = {}
            
            for key, value in option.items():
                if key in ["id", "name", "description"]:
                    continue
                
                if isinstance(value, (int, float)):
                    # 数值型：直接使用，考虑权重
                    weight = self.criteria_weights.get(key, 1.0)
                    weighted_score = value * weight
                    score += weighted_score
                    details[key] = weighted_score
                    count += 1
                elif isinstance(value, str):
                    # 字符串：情感编码
                    str_score = self._encode_string_value(value)
                    score += str_score
                    details[key] = str_score
                    count += 1
            
            avg_score = score / max(count, 1)
            scores.append((i, avg_score, details))
        
        # 选择最高分
        scores.sort(key=lambda x: x[1], reverse=True)
        best_idx, best_score, best_details = scores[0]
        
        # 计算置信度（与次优选项的差距）
        if len(scores) > 1:
            confidence = min(0.95, best_score / max(scores[1][1], 0.1))
        else:
            confidence = 0.8
        
        return {
            "choice": options[best_idx],
            "confidence": confidence,
            "reason": f"选项{best_idx+1}得分最高({best_score:.2f})",
            "all_scores": [(i, s, d) for i, s, d in scores],
            "best_score": best_score,
            "score_details": best_details
        }
    
    def _encode_string_value(self, value: str) -> float:
        """将字符串值编码为数值分数"""
        value_lower = value.lower()
        if value_lower in ["好", "优秀", "high", "good", "excellent"]:
            return 1.0
        elif value_lower in ["一般", "中等", "medium", "average"]:
            return 0.5
        elif value_lower in ["差", "低", "low", "bad", "poor"]:
            return 0.1
        else:
            return 0.3


class TaskInterface:
    """任务接口 - 统一的多任务处理入口（增强版）"""
    
    def __init__(self, network, energy_engine, learner):
        self.network = network
        self.energy_engine = energy_engine
        self.learner = learner
        self.text_processor = TextProcessor()
        self.reasoning_engine = ReasoningEngine()
        self.decision_maker = DecisionMaker()
        self.task_history: List[Task] = []
        
        # 初始化一些默认事实、规则和知识
        self._init_default_facts()
        self._init_default_rules()
        self._init_default_knowledge()
    
    def _init_default_facts(self) -> None:
        """初始化默认事实库"""
        self.reasoning_engine.add_fact("系统状态", "运行中")
        self.reasoning_engine.add_fact("能量水平", "正常")
        
    def _init_default_rules(self) -> None:
        """初始化默认推理规则（新增多条规则）"""
        # 规则1：高能量规则
        def high_energy_condition(facts):
            return facts.get("energy", 0) > 0.7
        
        def high_energy_conclusion(facts):
            return "系统处于高能量状态，适合处理复杂任务"
        
        self.reasoning_engine.add_rule("高能量规则", high_energy_condition, high_energy_conclusion)
        
        # 规则2：低能量规则
        def low_energy_condition(facts):
            return facts.get("energy", 1) < 0.3
        
        def low_energy_conclusion(facts):
            return "系统能量不足，应优先处理关键任务"
        
        self.reasoning_engine.add_rule("低能量规则", low_energy_condition, low_energy_conclusion)
        
        # 规则3：学习进步规则
        def learning_condition(facts):
            return facts.get("学习次数", 0) > 5
        
        def learning_conclusion(facts):
            return "系统通过学习得到提升，应尝试更复杂任务"
        
        self.reasoning_engine.add_rule("学习进步规则", learning_condition, learning_conclusion)
        
    def _init_default_knowledge(self) -> None:
        """初始化默认知识库"""
        self.reasoning_engine.add_knowledge({
            "concept": "AGI",
            "definition": "通用人工智能，能像人类一样执行任何智能任务",
            "category": "AI"
        })
        self.reasoning_engine.add_knowledge({
            "concept": "复合体理学",
            "definition": "研究复合体结构和演化规律的理论体系",
            "category": "Theory"
        })
    
    def process(self, task: Task) -> Task:
        """处理任务，返回完成的任务"""
        task.status = TaskStatus.PROCESSING
        start_time = time.time()
        
        try:
            if task.type == TaskType.TEXT_UNDERSTANDING:
                result = self._process_text_task(task)
            elif task.type == TaskType.SIMPLE_REASONING:
                result = self._process_reasoning_task(task)
            elif task.type == TaskType.DECISION_MAKING:
                result = self._process_decision_task(task)
            elif task.type == TaskType.PATTERN_MATCH:
                result = self._process_pattern_task(task)
            elif task.type == TaskType.NEURAL_PROCESS:
                result = self._process_neural_task(task)
            else:
                result = self._process_general_task(task)
            
            task.output = result
            task.confidence = result.get("confidence", 0.5) if isinstance(result, dict) else 0.5
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.output = {"error": str(e)}
            task.status = TaskStatus.FAILED
            task.confidence = 0.0
        
        task.processing_time = time.time() - start_time
        self.task_history.append(task)
        
        # 记录学习经验（真实学习：更新内部状态）
        # record_experience 会根据 performance_score 自动调用 adapt_parameters
        self.learner.record_experience(
            task_id=task.id,
            task_type=task.type.value,
            input_data=task.input_data,
            output_data=task.output,
            expected=task.expected_output
        )
        
        return task
    
    def _process_text_task(self, task: Task) -> Dict[str, Any]:
        """处理文本理解任务"""
        text = str(task.input_data)
        
        # 评估信息价值，分配能量
        value = self.energy_engine.evaluate_information_value(text, task.metadata)
        self.energy_engine.distribute_to_layer(LayerType.PERCEPTION, value * 0.5)
        
        # 理解文本（使用增强版处理器）
        understanding = self.text_processor.understand(text)
        
        # 消耗处理能量
        for unit in self.network.get_layer_units(LayerType.COGNITION):
            self.energy_engine.consume_for_processing(unit.id, 0.05)
        
        # 生成回复（如果需要）
        if task.metadata.get("generate_response", False):
            response = self.text_processor.generate_response(understanding)
            understanding["response"] = response
        
        return understanding
    
    def _process_reasoning_task(self, task: Task) -> Dict[str, Any]:
        """处理推理任务（增强版）"""
        query = str(task.input_data)
        
        # 分配能量到认知和决策层
        self.energy_engine.distribute_to_layer(LayerType.COGNITION, 0.3)
        self.energy_engine.distribute_to_layer(LayerType.DECISION, 0.2)
        
        # 执行推理（使用增强版推理引擎）
        result = self.reasoning_engine.reason(query, task.metadata)
        
        # 消耗能量
        for unit in self.network.get_layer_units(LayerType.COGNITION):
            self.energy_engine.consume_for_processing(unit.id, 0.08)
        
        return result
    
    def _process_decision_task(self, task: Task) -> Dict[str, Any]:
        """处理决策任务"""
        options = task.input_data if isinstance(task.input_data, list) else []
        
        # 分配能量到决策层
        self.energy_engine.distribute_to_layer(LayerType.DECISION, 0.4)
        
        # 做出决策
        result = self.decision_maker.decide(options, task.metadata)
        
        # 消耗能量
        for unit in self.network.get_layer_units(LayerType.DECISION):
            self.energy_engine.consume_for_processing(unit.id, 0.1)
        
        return result
    
    def _process_pattern_task(self, task: Task) -> Dict[str, Any]:
        """处理模式匹配任务"""
        data = task.input_data
        
        # 简单模式匹配
        patterns = task.metadata.get("patterns", [])
        matches = []
        
        if isinstance(data, str):
            for pattern in patterns:
                if pattern in data:
                    matches.append(pattern)
        
        return {
            "matches": matches,
            "match_count": len(matches),
            "confidence": len(matches) / max(len(patterns), 1)
        }
    
    def _process_neural_task(self, task: Task) -> Dict[str, Any]:
        """处理神经网络任务（预留接口）"""
        # 这里是神经网络处理的占位符
        # 实际实现会在 neural_network.py 中完成
        return {
            "type": "neural_processing",
            "status": "placeholder",
            "message": "神经网络处理接口已就绪，等待集成",
            "confidence": 0.3
        }
    
    def _process_general_task(self, task: Task) -> Dict[str, Any]:
        """处理通用任务"""
        # 默认：尝试作为文本处理
        return self._process_text_task(task)
    
    def create_task(self, task_type: str, input_data: Any, 
                   expected_output: Any = None, **metadata) -> Task:
        """创建任务"""
        import uuid
        task_id = str(uuid.uuid4())[:8]
        t_type = TaskType(task_type) if task_type in [t.value for t in TaskType] else TaskType.GENERAL
        
        return Task(
            id=task_id,
            type=t_type,
            input_data=input_data,
            expected_output=expected_output,
            metadata=metadata
        )
    
    def get_task_summary(self) -> Dict[str, Any]:
        """获取任务处理摘要"""
        if not self.task_history:
            return {"total": 0}
        
        completed = sum(1 for t in self.task_history if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.task_history if t.status == TaskStatus.FAILED)
        avg_time = sum(t.processing_time for t in self.task_history) / len(self.task_history)
        avg_confidence = sum(t.confidence for t in self.task_history) / len(self.task_history)
        
        return {
            "total": len(self.task_history),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / len(self.task_history),
            "avg_processing_time": avg_time,
            "avg_confidence": avg_confidence
        }
