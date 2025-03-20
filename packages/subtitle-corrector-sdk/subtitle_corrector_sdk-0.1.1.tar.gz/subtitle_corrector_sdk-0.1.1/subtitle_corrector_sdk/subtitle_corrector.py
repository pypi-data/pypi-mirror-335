#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医学视频字幕校对系统
用于自动校正医学视频字幕中的术语错误，同时保持原始字幕结构和时间戳不变
支持处理分割成多个部分的字幕文件
"""

import os
import json
import requests
import time
import shutil
import zipfile
from datetime import datetime
import logging
import re
import glob
import pkg_resources

# 配置日志
os.makedirs("logs", exist_ok=True)  # 确保logs目录存在
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/subtitle_corrector.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SubtitleCorrector")

class SubtitleCorrector:
    """医学字幕校对器类"""
    
    def __init__(self, api_key,input_dir,output_dir,config_file="config.json"):
        """初始化字幕校对器
        
        Args:
            config_file: 配置文件路径
        """
        self.api_key = api_key
        self.input_dir = input_dir
        self.output_dir = output_dir

        # 加载配置
        self.load_config(config_file)
        
        # 加载错误术语库
        self.load_error_terms()
        
        # 创建必要的目录
        self.create_directories()
        
        # 生成校对提示词
        self.generate_prompt()
    
    def load_config(self, config_file):
        """加载配置文件
        
        Args:
            config_file: 配置文件路径
        """
        try:
            config_path = pkg_resources.resource_filename(__name__, config_file)
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # 设置API参数

            self.api_url = self.config.get("api_url")
            self.model = self.config.get("model")
            
            # 设置目录路径
            self.backup_dir = self.config.get("backup_dir", "backup")
            self.error_terms_file = self.config.get("error_terms_file", "error_terms_library.json")
            
            # 字幕特定配置
            self.window_size = self.config.get("window_size", 30)  # 处理窗口大小（字幕块数量）
            self.file_pattern = self.config.get("file_pattern", "*.srt")  # 文件名匹配模式
            self.preserve_original_index = self.config.get("preserve_original_index", True)  # 是否保留原始序号
            
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise
    
    def load_error_terms(self):
        """加载错误术语库"""
        try:
            error_terms_path = pkg_resources.resource_filename(__name__, self.error_terms_file)
            with open(self.error_terms_file, 'r', encoding='utf-8') as f:
                self.error_terms = json.load(f)
            logger.info(f"错误术语库加载成功，共{sum(len(terms) for terms in self.error_terms.values())}个术语")
        except Exception as e:
            logger.error(f"加载错误术语库失败: {str(e)}")
            raise
    
    def create_directories(self):
        """创建必要的目录"""
        for directory in [self.input_dir, self.output_dir, self.backup_dir]:
            os.makedirs(directory, exist_ok=True)
        logger.info("目录创建成功")

    def generate_prompt(self):
        """生成字幕校对提示词"""
        try:
            prompt_path = pkg_resources.resource_filename(__name__, "prompt.txt")
            with open("prompt.txt", "r", encoding="utf-8") as file:
                self.system_prompt = file.read()
            logger.info("字幕校对提示词生成成功")
        except FileNotFoundError:
            logger.error("提示词文件未找到，请检查文件路径")
        except Exception as e:
            logger.error(f"生成字幕校对提示词时发生错误：{e}")
    
    def backup_files(self):
        """备份文件"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            backup_filename = f"subtitle_corrector_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                # 备份输入文件
                for root, _, files in os.walk(self.input_dir):
                    for file in files:
                        if file.lower().endswith('.srt'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(self.input_dir))
                            zipf.write(file_path, arcname)
                
                # 备份错误术语库
                zipf.write(self.error_terms_file, os.path.basename(self.error_terms_file))
                
                # 备份配置文件
                zipf.write("config.json", "config.json")
            
            logger.info(f"文件备份成功: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"文件备份失败: {str(e)}")
            return False
    
    def parse_srt(self, file_path):
        """解析SRT格式字幕文件
        
        Args:
            file_path: 字幕文件路径
            
        Returns:
            list: 字幕对象列表
        """
        try:
            subtitles = []
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按字幕块分割
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:  # 确保至少有序号、时间戳和文本
                    index = lines[0]
                    time_line = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # 解析时间戳
                    time_match = re.match(r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)', time_line)
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        
                        subtitle = {
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text
                        }
                        
                        subtitles.append(subtitle)
            
            logger.info(f"成功解析字幕文件，共{len(subtitles)}个字幕块")
            return subtitles
        except Exception as e:
            logger.error(f"解析字幕文件失败: {str(e)}")
            raise
    
    def write_srt(self, subtitles, output_path):
        """将字幕对象列表写入SRT文件
        
        Args:
            subtitles: 字幕对象列表
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, subtitle in enumerate(subtitles):
                    # 写入序号 (使用原始序号)
                    f.write(f"{subtitle['index']}\n")
                    
                    # 写入时间戳
                    f.write(f"{subtitle['start_time']} --> {subtitle['end_time']}\n")
                    
                    # 写入文本
                    f.write(f"{subtitle['text']}\n\n")
            
            logger.info(f"字幕文件保存成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"保存字幕文件失败: {str(e)}")
            return False
    
    def call_deepseek_api_with_subtitle_prompt(self, subtitle_text, max_retries=5, retry_delay=5, timeout=180):
        """调用DeepSeek API进行字幕校正
        
        Args:
            subtitle_text: 要处理的字幕文本
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            timeout: API请求超时时间（秒）
            
        Returns:
            str: API返回的校正后文本
        """
        # 构建请求数据 - 使用原始格式，确保与火山引擎API兼容
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": subtitle_text}
            ],
            "max_tokens": 2048,
            "temperature": 0,
            "top_p": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        # 设置HTTP头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 定义重试计数器
        retry_count = 0
        last_exception = None
        
        # 添加重试逻辑
        while retry_count < max_retries:
            try:
                # 发送请求
                logger.info(f"正在调用API校正字幕（尝试 {retry_count + 1}/{max_retries}）...")
                
                # 增加超时时间以应对大型字幕块
                response = requests.post(self.api_url, headers=headers, json=data, timeout=timeout)
                
                # 记录API响应状态和头信息
                logger.info(f"API响应状态码: {response.status_code}")
                logger.debug(f"API响应头: {response.headers}")
                
                # 保存原始API响应供后续分析
                raw_response_text = response.text
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    logger.error(f"API调用失败: HTTP {response.status_code}")
                    
                    # 如果启用详细日志，记录API错误响应内容
                    logging_config = self.config.get("logging", {})
                    enable_detailed_logs = logging_config.get("enable_detailed_logs", True)
                    if enable_detailed_logs:
                        logger.error(f"API错误响应内容: {raw_response_text}")
                    
                    # 尝试解析错误响应
                    try:
                        error_json = response.json()
                        if 'error' in error_json:
                            logger.error(f"API错误类型: {error_json['error'].get('type', 'unknown')}")
                            logger.error(f"API错误消息: {error_json['error'].get('message', 'no message')}")
                    except:
                        logger.error("无法解析API错误响应为JSON格式")
                    
                    # 增加重试次数并等待
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"将在 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        error_msg = f"API多次调用失败: HTTP {response.status_code}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                
                # 解析JSON响应
                try:
                    response_json = response.json()
                    #print(response_json)
                    
                    # 记录完整的API响应（用于调试）
                    logging_config = self.config.get("logging", {})
                    enable_detailed_logs = logging_config.get("enable_detailed_logs", True)
                    if enable_detailed_logs:
                        logger.debug(f"API完整响应: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                    
                    # 检查是否有错误
                    if "error" in response_json:
                        error_message = response_json.get("error", {}).get("message", "未知错误")
                        logger.error(f"API返回错误: {error_message}")
                        
                        # 增加重试次数并等待
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.info(f"将在 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            error_msg = f"API多次调用失败: {error_message}"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                    
                    # 检查响应是否包含必要的字段
                    if "choices" not in response_json or not response_json["choices"]:
                        logger.error("API响应格式不正确，缺少choices字段")
                        
                        # 增加重试次数并等待
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.info(f"将在 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            error_msg = "API多次返回格式不正确的响应"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                    
                    # 获取内容
                    corrected_text = response_json["choices"][0]["message"]["content"]
                    
                    # 记录token使用情况（如果有）
                    if "usage" in response_json:
                        usage = response_json["usage"]
                        logger.info(f"API使用情况 - 输入tokens: {usage.get('prompt_tokens', 'N/A')}, "
                                  f"输出tokens: {usage.get('completion_tokens', 'N/A')}, "
                                  f"总tokens: {usage.get('total_tokens', 'N/A')}")
                    
                    # 检查完成原因（如果有）
                    finish_reason = response_json["choices"][0].get("finish_reason")
                    if finish_reason:
                        logger.info(f"API完成原因: {finish_reason}")
                        if finish_reason == "length":
                            logger.warning("警告: API响应因达到最大长度限制而被截断")
                    
                    # 对AI返回的内容应用错误术语库精确替换
                    logger.info("正在应用错误术语库精确替换...")
                    corrected_text, replacement_details = self.apply_term_corrections(corrected_text)
                    
                    # 后处理：移除可能的注释
                    corrected_text = self.remove_annotations(corrected_text)
                    
                    # 返回校正后的文本和替换详情
                    return corrected_text, replacement_details
                    
                except (KeyError, json.JSONDecodeError) as e:
                    logger.error(f"API响应解析错误: {str(e)}")
                    
                    # 如果启用详细日志，记录API原始响应内容
                    logging_config = self.config.get("logging", {})
                    enable_detailed_logs = logging_config.get("enable_detailed_logs", True)
                    if enable_detailed_logs:
                        logger.error(f"API原始响应内容: {raw_response_text}")
                    
                    # 增加重试次数并等待
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"将在 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        error_msg = f"API多次响应解析失败: {str(e)}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
            except requests.RequestException as e:
                logger.error(f"API请求异常: {str(e)}")
                last_exception = e
                
                # 增加重试次数并等待
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                logger.error(f"调用API时发生未知错误: {str(e)}")
                last_exception = e
                
                # 增加重试次数并等待
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    continue
            
        # 如果所有重试都失败，抛出最后一个异常
        error_msg = f"API在 {max_retries} 次尝试后仍然失败: {str(last_exception)}"
        logger.error(error_msg)
        raise Exception(error_msg)
        
    def remove_annotations(self, text):
        """移除文本中可能的注释
        
        Args:
            text: 待处理的文本
            
        Returns:
            str: 处理后的文本
        """
        # 保存原始文本，以便在处理失败时返回
        original_text = text
        
        # 移除"修正说明："及其后续内容
        if "修正说明：" in text:
            parts = text.split("修正说明：", 1)
            text = parts[0].rstrip()
        
        # 移除"修改说明"及其后续内容（符合规则要求）
        if "修改说明（符合规则要求）：" in text:
            parts = text.split("修改说明（符合规则要求）：", 1)
            text = parts[0].rstrip()
        
        # 移除"主要修改内容："及其后续内容
        if "主要修改内容：" in text:
            parts = text.split("主要修改内容：", 1)
            text = parts[0].rstrip()
        
        # 移除常见的注释标记及其内容
        annotation_patterns = [
            r"注释：.*?(?=\n|$)",
            r"说明：.*?(?=\n|$)",
            r"备注：.*?(?=\n|$)",
            r"修改列表：.*?(?=\n|$)",
            r"主要修改内容：.*?(?=\n|$)",
            r"修改内容：.*?(?=\n|$)",
            r"[\(（]注：.*?[\)）]",
            r"[\(（]注:.*?[\)）]",
            r"[\(（]修改:.*?[\)）]",
            r"[\(（]修改：.*?[\)）]",
            r"[\(（]校正:.*?[\)）]",
            r"[\(（]校正：.*?[\)）]",
            r"[\[【]修正.*?[\]】]",
            r"[\{「]修正.*?[\}」]",
            r"（注：.*?）",
            r"\(注：.*?\)",
            r"（注:.*?）",
            r"\(注:.*?\)",
            # 添加识别API返回的指令性注释的模式
            r"[\(（]维持原始.*?[\)）]",
            r"[\(（]保持.*?不变[\)）]",
            r"[\(（]严格保留.*?[\)）]",
            r"[\(（]禁止.*?[\)）]",
            r"[\(（]输出保持.*?[\)）]",
            r"[\(（]最终块.*?[\)）]",
            r"[\(（]此处保留.*?[\)）]"
        ]
        
        for pattern in annotation_patterns:
            text = re.sub(pattern, "", text, flags=re.MULTILINE)
        
        # 移除多余的空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # 移除字幕块之间的注释内容
        # 查找所有符合SRT格式的字幕块
        srt_blocks = re.findall(r'^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n[\s\S]*?(?=\n\n\d+|\Z)', text, re.MULTILINE)
        
        if srt_blocks:
            # 如果找到了字幕块，只保留这些块
            clean_text = "\n\n".join(srt_blocks)
            return clean_text.strip()
        else:
            # 如果没有找到符合SRT格式的字幕块，尝试使用更宽松的正则表达式
            srt_blocks_loose = re.findall(r'^\d+\s*\n\d+.*?-->\s*\d+.*?\n[\s\S]*?(?=\n\n\d+|\Z)', text, re.MULTILINE)
            if srt_blocks_loose:
                clean_text = "\n\n".join(srt_blocks_loose)
                return clean_text.strip()
            else:
                # 如果仍然没有找到，返回处理后的文本
                logger.warning("无法从API响应中提取SRT格式字幕块，返回处理后的文本")
                # 返回经过基本清理的文本，而不是可能过度清理的文本
                return original_text.strip()
    
    def extract_blocks_from_text(self, text):
        """从文本中提取字幕块
        
        Args:
            text: 字幕文本
            
        Returns:
            list: 字幕块列表，每个块是一个字典，包含index、start_time、end_time和text字段
        """
        # 使用空行分割文本
        blocks = re.split(r'\n\s*\n', text.strip())
        
        subtitles = []
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:  # 确保至少有序号、时间戳和文本
                try:
                    # 提取序号
                    index = lines[0].strip()
                    
                    # 提取时间戳
                    time_line = lines[1]
                    time_parts = time_line.split(' --> ')
                    if len(time_parts) != 2:
                        logger.warning(f"无效的时间戳格式: {time_line}")
                        continue
                    
                    start_time = time_parts[0].strip()
                    end_time = time_parts[1].strip()
                    
                    # 提取文本内容（第3行及以后的内容）
                    text = '\n'.join(lines[2:])
                    
                    # 添加到字幕列表
                    subtitles.append({
                        'index': index,
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text
                    })
                except Exception as e:
                    logger.warning(f"解析字幕块时发生异常: {str(e)}, 块内容: {block}")
        
        return subtitles
    
    def get_output_path(self, file_path):
        """获取输出文件路径
        
        Args:
            file_path: 输入文件路径
            
        Returns:
            str: 输出文件路径
        """
        # 获取文件名和扩展名
        file_name = os.path.basename(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        
        # 创建输出文件路径 (添加"_corrected"后缀)
        output_file_name = f"{file_base}_corrected{file_ext}"
        output_path = os.path.join(self.output_dir, output_file_name)
        
        return output_path
    
    def process_subtitle_file(self, file_path, custom_window_size=None, start_window=None, end_window=None):
        """处理字幕文件
        
        Args:
            file_path: 字幕文件路径
            custom_window_size: 自定义窗口大小，如果提供则覆盖配置中的窗口大小
            start_window: 开始处理的窗口索引（从1开始），如果不提供则从第一个窗口开始
            end_window: 结束处理的窗口索引（包含），如果不提供则处理到最后一个窗口
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 获取输出文件路径
            output_path = self.get_output_path(file_path)
            
            # 解析字幕文件
            subtitles = self.parse_srt(file_path)
            
            # 使用自定义窗口大小（如果提供）
            window_size = custom_window_size if custom_window_size is not None else self.window_size
            
            # 确保窗口大小是正整数
            if not isinstance(window_size, int) or window_size <= 0:
                logger.error(f"窗口大小必须是正整数，当前值: {window_size}")
                return False
            
            # 按窗口分组处理字幕块
            corrected_subtitles = []
            
            # 记录使用的窗口大小
            logger.info(f"使用窗口大小: {window_size}")
            
            # 获取日志设置
            logging_config = self.config.get("logging", {})
            enable_subtitle_logs = logging_config.get("enable_subtitle_logs", True)
            enable_detailed_logs = logging_config.get("enable_detailed_logs", True)
            log_dir = logging_config.get("log_dir", "subtitle_logs")
            
            # 如果启用了日志记录
            detailed_log_path = None
            if enable_subtitle_logs:
                # 创建详细日志目录
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_dir)
                os.makedirs(log_dir, exist_ok=True)
                
                # 创建详细日志文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                detailed_log_path = os.path.join(log_dir, f"subtitle_comparison_{timestamp}.log")
                
                with open(detailed_log_path, 'w', encoding='utf-8') as log_file:
                    log_file.write(f"字幕文件: {file_path}\n")
                    log_file.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    log_file.write(f"窗口大小: {window_size}\n")
                    if start_window is not None or end_window is not None:
                        log_file.write(f"处理窗口范围: {start_window if start_window is not None else 1} 到 {end_window if end_window is not None else '最后'}\n")
                    log_file.write("\n")
                    log_file.write("=" * 80 + "\n\n")
                
                logger.info(f"日志记录已启用，日志文件: {detailed_log_path}")
                logger.info(f"详细API响应记录: {'已启用' if enable_detailed_logs else '已禁用'}")
            else:
                logger.info("日志记录已禁用")
            
            # 计算窗口总数
            total_windows = (len(subtitles) + window_size - 1) // window_size
            
            # 确定开始和结束窗口索引
            start_idx = (start_window - 1) if start_window is not None else 0
            end_idx = end_window if end_window is not None else total_windows
            
            # 确保索引在有效范围内
            start_idx = max(0, start_idx)
            end_idx = min(total_windows, end_idx)
            
            logger.info(f"总窗口数: {total_windows}, 处理窗口范围: {start_idx + 1} 到 {end_idx}")
            
            # 如果是指定窗口处理模式，先复制所有字幕作为基础，然后只替换指定窗口的部分
            if start_window is not None or end_window is not None:
                corrected_subtitles = subtitles.copy()
            
            # 遍历每个窗口
            for window_idx in range(total_windows):
                # 计算当前窗口的起始和结束索引
                i = window_idx * window_size
                
                # 获取当前窗口的字幕块
                window_subtitles = subtitles[i:min(i+window_size, len(subtitles))]
                
                # 如果不在处理范围内，则跳过
                if window_idx < start_idx or window_idx >= end_idx:
                    if start_window is not None or end_window is not None:
                        logger.info(f"跳过窗口 {window_idx + 1} (不在处理范围内)")
                    continue
                
                # 组合文本为标准SRT格式
                combined_text = ""
                for subtitle in window_subtitles:
                    combined_text += f"{subtitle['index']}\n"
                    combined_text += f"{subtitle['start_time']} --> {subtitle['end_time']}\n"
                    combined_text += f"{subtitle['text']}\n\n"
                
                # 记录原始文本，用于调试
                logger.debug(f"发送到API的原始文本:\n{combined_text}")
                
                # 调用API进行校正
                try:
                    corrected_text, replacement_details = self.call_deepseek_api_with_subtitle_prompt(combined_text)
                    
                    # 记录API返回的原始响应，用于调试
                    logger.debug(f"API返回的原始响应:\n{corrected_text}")
                    
                    # 解析校正后的文本，提取字幕块
                    api_blocks = self.extract_blocks_from_text(corrected_text)
                    
                    # 创建原始字幕块的索引映射
                    original_blocks_dict = {subtitle['index']: subtitle for subtitle in window_subtitles}
                    
                    # 创建API返回块的索引映射
                    api_blocks_dict = {block['index']: block for block in api_blocks}
                    
                    # 准备最终结果列表
                    window_final_blocks = []
                    missing_indices = []
                    
                    # 为每个字幕块分配术语替换详情
                    # 由于术语替换是在整个窗口文本上进行的，我们需要分析每个替换，判断它属于哪个字幕块
                    block_replacements = {}
                    
                    # 初始化每个块的替换列表
                    for block in api_blocks:
                        block_replacements[block['index']] = []
                    
                    # 为每个替换找到所属的字幕块
                    for replacement in replacement_details:
                        parts = replacement.split(" → ")
                        if len(parts) == 2:
                            error_term = parts[0]
                            correct_term = parts[1]
                            
                            # 检查每个块中是否包含这个替换
                            for block in api_blocks:
                                if error_term in original_blocks_dict.get(block['index'], {}).get('text', '') and correct_term in block['text']:
                                    block_replacements[block['index']].append(replacement)
                    
                    # 记录详细对比日志
                    if enable_subtitle_logs:
                        with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"处理窗口 {window_idx + 1} [块索引 {i+1} 到 {min(i+window_size, len(subtitles))}]\n")
                            log_file.write("-" * 80 + "\n\n")
                            
                            # 记录API返回的原始内容到详细日志
                            if enable_detailed_logs:
                                log_file.write("API响应原始内容:\n")
                                log_file.write("-" * 40 + "\n")
                                log_file.write(f"{corrected_text}\n")
                                log_file.write("-" * 40 + "\n\n")
                    
                    # 遍历原始字幕块的索引顺序
                    for original_block in window_subtitles:
                        index = original_block['index']
                        
                        # 尝试从API结果中找到对应索引的块
                        if index in api_blocks_dict:
                            # 如果找到对应索引的块，使用API返回的内容
                            api_block = api_blocks_dict[index]
                            window_final_blocks.append(api_block)
                            
                            # 记录详细对比日志
                            if enable_subtitle_logs:
                                with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                                    log_file.write(f"字幕块 #{index} - 使用API返回内容\n")
                                    log_file.write(f"原始文本: {original_block['text']}\n")
                                    log_file.write(f"API返回: {api_block['text']}\n")
                                    
                                    # 添加术语精确替换信息
                                    if index in block_replacements and block_replacements[index]:
                                        log_file.write(f"术语精确替换: {', '.join(block_replacements[index])}\n")
                                    
                                    log_file.write(f"状态: {'已修改' if original_block['text'] != api_block['text'] else '未修改'}\n")
                                    log_file.write(f"最终使用: {api_block['text']}\n\n")
                        else:
                            # 如果没找到，使用原始块
                            window_final_blocks.append(original_block)
                            missing_indices.append(index)
                            
                            # 记录详细对比日志
                            if enable_subtitle_logs:
                                with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                                    log_file.write(f"字幕块 #{index} - 使用原始内容（API未返回）\n")
                                    log_file.write(f"原始文本: {original_block['text']}\n")
                                    log_file.write(f"API返回: 未返回\n")
                                    log_file.write(f"状态: 使用原始内容\n")
                                    log_file.write(f"最终使用: {original_block['text']}\n\n")
                    
                    # 记录缺失的块
                    if missing_indices:
                        logger.warning(f"API返回结果中缺少以下字幕块，已使用原始内容: {missing_indices}")
                    
                    # 如果是指定窗口处理模式，则只替换该窗口的内容
                    if start_window is not None or end_window is not None:
                        # 计算在完整结果列表中的起始索引
                        start_pos = i
                        # 替换对应位置的字幕块
                        for idx, block in enumerate(window_final_blocks):
                            if start_pos + idx < len(corrected_subtitles):
                                corrected_subtitles[start_pos + idx] = block
                    else:
                        # 添加到结果列表
                        corrected_subtitles.extend(window_final_blocks)
                    
                    # 输出进度
                    progress = (window_idx + 1) / (end_idx - start_idx) * 100
                    logger.info(f"字幕校正进度: {progress:.2f}% (窗口 {window_idx + 1}/{end_idx})")
                    
                    # 在详细日志中添加分隔符
                    if enable_subtitle_logs:
                        with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write("=" * 80 + "\n\n")
                except Exception as api_error:
                    # 在API调用失败时记录错误
                    logger.error(f"API调用失败: {str(api_error)}")
                    
                    # 记录API错误到详细日志
                    if enable_subtitle_logs:
                        with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"处理窗口 {window_idx + 1} [块索引 {i+1} 到 {min(i+window_size, len(subtitles))}]\n")
                            log_file.write("-" * 80 + "\n\n")
                            log_file.write("API调用错误:\n")
                            log_file.write("-" * 40 + "\n")
                            log_file.write(f"错误信息: {str(api_error)}\n")
                            log_file.write(f"错误类型: {type(api_error).__name__}\n")
                            log_file.write("-" * 40 + "\n\n")
                    
                    # 记录严重错误并终止程序
                    error_message = f"API调用失败，程序终止执行！错误信息: {str(api_error)}"
                    logger.critical(error_message)
                    
                    # 在日志中添加分隔符
                    if enable_subtitle_logs:
                        with open(detailed_log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write("=" * 80 + "\n")
                            log_file.write("程序因API调用失败而终止执行！\n")
                            log_file.write("=" * 80 + "\n\n")
                    
                    # 直接抛出异常终止程序
                    raise RuntimeError(error_message)
            
            # 保存校正后的字幕文件
            self.write_srt(corrected_subtitles, output_path)
            
            logger.info(f"字幕文件处理成功: {file_path} -> {output_path}")
            if enable_subtitle_logs:
                logger.info(f"详细对比日志已保存到: {detailed_log_path}")
            return True
        except Exception as e:
            logger.error(f"字幕文件处理失败: {str(e)}")
            return False
    
    def apply_term_corrections(self, text):
        """对AI校正后的文本应用错误术语库精确替换"""
        corrected_text = text
        replacements_made = 0
        
        # 需要处理的术语类别
        categories_to_process = [
            "解剖与组织术语", "影像与检查术语", "实验室检查术语", "微生物术语",
            "临床症状与体征术语", "疾病名称规范", "药物名称术语", "医学专业缩写",
            "音译医学术语", "通用听写误差", "综合医学术语", "特殊品牌替换"
        ]
        
        # 记录替换情况
        replacement_details = []
        
        # 遍历需要处理的术语类别
        for category in categories_to_process:
            if category in self.error_terms:
                for term in self.error_terms[category]:
                    # 检查是否包含箭头符号（表示替换关系）
                    if "→" in term or "->" in term:
                        # 分割错误术语和正确术语
                        parts = term.replace("->", "→").split("→")
                        if len(parts) == 2:
                            error_term, correct_term = parts[0].strip(), parts[1].strip()
                            
                            # 检查文本中是否包含该错误术语
                            if error_term in corrected_text:
                                # 执行替换前的文本
                                before = corrected_text
                                
                                # 执行精确替换
                                corrected_text = corrected_text.replace(error_term, correct_term)
                                
                                # 如果文本有变化，记录替换情况
                                if before != corrected_text:
                                    replacements_made += 1
                                    replacement_details.append(f"{error_term} → {correct_term}")
        
        # 记录替换结果
        if replacements_made > 0:
            logger.info(f"术语库精确替换完成，共替换了{replacements_made}个术语")
            logger.debug(f"替换详情: {', '.join(replacement_details)}")
        else:
            logger.info("术语库精确替换完成，未发现需要替换的术语")
        
        # 返回替换后的文本和替换详情
        return corrected_text, replacement_details
    
    def process_all_files(self):
        """处理所有字幕文件"""
        try:
            # 备份文件
            self.backup_files()
            
            # 获取输入目录中的所有匹配文件
            file_pattern = os.path.join(self.input_dir, self.file_pattern)
            files = glob.glob(file_pattern)
            
            # 统计
            total_files = len(files)
            processed_files = 0
            success_files = 0
            
            logger.info(f"开始处理字幕文件，共{total_files}个文件")
            
            # 处理每个文件
            for file_path in files:
                file_name = os.path.basename(file_path)
                
                logger.info(f"正在处理字幕文件: {file_name}")
                
                # 处理文件
                if self.process_subtitle_file(file_path):
                    success_files += 1
                
                processed_files += 1
                
                # 输出进度
                progress = processed_files / total_files * 100
                logger.info(f"文件处理进度: {progress:.2f}% ({processed_files}/{total_files})")
            
            logger.info(f"字幕文件处理完成，成功: {success_files}，失败: {processed_files - success_files}")
            return True
        except Exception as e:
            logger.error(f"处理字幕文件时发生错误: {str(e)}")
            return False

def main():
    """主函数"""
    try:
        logger.info("医学视频字幕校对系统启动")
        
        # 创建校对器
        corrector = SubtitleCorrector()
        
        # 处理所有文件
        corrector.process_all_files()
        
        logger.info("医学视频字幕校对系统结束")
    except Exception as e:
        logger.error(f"程序运行异常: {str(e)}")

if __name__ == "__main__":
    main()
