import re


def clean_code_output(code: str) -> str:
    """
    清理代码生成器的输出
    
    Args:
        code: 原始代码输出
        
    Returns:
        清理后的代码
    """
    # 移除开头的markdown标记
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^```\s*\n', '', code, flags=re.MULTILINE)
    
    # 移除结尾的markdown标记
    code = re.sub(r'\n```$', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    # 移除开头的执行说明
    code = re.sub(r'^要运行此代码.*?\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^运行方式.*?\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^使用方法.*?\n', '', code, flags=re.MULTILINE)
    
    # 移除开头的空行
    code = code.lstrip('\n')
    
    return code


def clean_article_output(article: str) -> str:
    """
    清理文章生成器的输出
    
    Args:
        article: 原始文章输出
        
    Returns:
        清理后的文章
    """
    # 移除开头的执行说明
    article = re.sub(r'^要运行此代码.*?\n', '', article, flags=re.MULTILINE)
    article = re.sub(r'^运行方式.*?\n', '', article, flags=re.MULTILINE)
    article = re.sub(r'^使用方法.*?\n', '', article, flags=re.MULTILINE)
    article = re.sub(r'^保存为.*?\n', '', article, flags=re.MULTILINE)
    
    # 确保代码块正确闭合
    # 查找未闭合的代码块
    code_blocks = re.findall(r'```python\n(.*?)\n```', article, re.DOTALL)
    open_blocks = len(re.findall(r'```python', article))
    close_blocks = len(re.findall(r'```', article)) - open_blocks
    
    # 如果有未闭合的代码块，尝试修复
    if open_blocks > close_blocks:
        article += '\n```'
    
    # 移除开头的空行
    article = article.lstrip('\n')
    
    return article


def clean_search_query(query: str) -> str:
    """
    清理搜索查询，提取核心关键词
    
    Args:
        query: 原始任务描述
        
    Returns:
        清理后的搜索查询
    """
    # 移除常见的前缀
    prefixes = ['写一篇', '撰写', '关于', '分析', '实现', '开发', '生成', '帮我', '请', '用']
    for prefix in prefixes:
        if query.startswith(prefix):
            query = query[len(prefix):]
            break
    
    # 移除常见的后缀
    suffixes = ['的文章', '的报告', '的内容', '的代码', '的算法', '的程序']
    for suffix in suffixes:
        if query.endswith(suffix):
            query = query[:-len(suffix)]
            break
    
    # 清理标点符号
    query = query.strip()
    query = query.rstrip('？?。.！!')
    
    return query


def fix_fstring_issues(code: str) -> str:
    """
    修复 f-string 中的语法问题
    
    Args:
        code: 原始代码
        
    Returns:
        修复后的代码
    """
    # 查找所有 f-string
    pattern = r'f"([^"]*?\{[^}]*\}[^"]*?)"'
    
    def fix_fstring(match):
        content = match.group(1)
        # 检查是否包含复杂表达式
        if re.search(r'\{[^}]*[.()[\]]', content):
            # 提取变量名
            variables = re.findall(r'\{([^}]+)\}', content)
            # 生成修复后的代码
            result = []
            for var in variables:
                # 如果是简单变量，保留
                if not re.search(r'[.()[\]]', var):
                    result.append(f'{{{var}}}')
                else:
                    # 复杂表达式，需要先赋值
                    var_name = re.sub(r'[^a-zA-Z0-9_]', '_', var)
                    result.append(f'{{{var_name}}}')
            return f'f"{" ".join(result)}"'
        return match.group(0)
    
    return re.sub(pattern, fix_fstring, code)
