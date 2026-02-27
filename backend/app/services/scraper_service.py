"""
网页抓取服务
从 URL 提取网页正文内容
"""
import logging
import re
from typing import Optional, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScraperService:
    """网页内容抓取服务"""
    
    # 允许抓取的域名白名单（可根据需要扩展）
    ALLOWED_DOMAINS = [
        # 新闻媒体
        "bbc.com", "www.bbc.com",
        "cnn.com", "www.cnn.com",
        "nytimes.com", "www.nytimes.com",
        "theguardian.com", "www.theguardian.com",
        "reuters.com", "www.reuters.com",
        "economist.com", "www.economist.com",
        # 教育资源
        "ted.com", "www.ted.com",
        "medium.com", "www.medium.com",
        "wikipedia.org", "en.wikipedia.org",
        # 技术博客
        "dev.to", "www.dev.to",
        "hackernews.com",
        "techcrunch.com", "www.techcrunch.com",
        # 通用
        "github.com", "www.github.com",
    ]
    
    # 需要移除的标签
    REMOVE_TAGS = [
        "script", "style", "nav", "header", "footer", 
        "aside", "form", "iframe", "noscript", "svg",
        "button", "input", "select", "textarea"
    ]
    
    def __init__(self):
        self.timeout = 15.0  # 请求超时时间
        self.max_content_length = 500000  # 最大内容长度 500KB
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        验证 URL 是否合法
        
        Returns:
            (is_valid, message)
        """
        try:
            parsed = urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ["http", "https"]:
                return False, "仅支持 HTTP/HTTPS 链接"
            
            # 检查域名
            if not parsed.netloc:
                return False, "无效的 URL 格式"
            
            # 检查是否在白名单中（可选，暂时放开限制）
            # domain = parsed.netloc.lower()
            # if domain not in self.ALLOWED_DOMAINS:
            #     return False, f"暂不支持该网站，支持的网站：{', '.join(self.ALLOWED_DOMAINS[:5])}..."
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False, f"URL 格式错误: {str(e)}"
    
    async def fetch_content(self, url: str) -> Tuple[str, str]:
        """
        抓取网页内容
        
        Args:
            url: 网页 URL
            
        Returns:
            (title, content) 标题和正文内容
            
        Raises:
            ValueError: 抓取失败时抛出
        """
        # 验证 URL
        is_valid, message = self.validate_url(url)
        if not is_valid:
            raise ValueError(message)
        
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                max_redirects=5
            ) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": self.user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
                    }
                )
                
                # 检查状态码
                if response.status_code != 200:
                    raise ValueError(f"网页请求失败: HTTP {response.status_code}")
                
                # 检查内容类型
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type.lower():
                    raise ValueError("该链接不是网页内容")
                
                # 检查内容长度
                content_length = len(response.content)
                if content_length > self.max_content_length:
                    raise ValueError("网页内容过大，请选择较短的文章")
                
                # 解析 HTML
                html_content = response.text
                title, content = self._extract_content(html_content)
                
                if not content or len(content.strip()) < 100:
                    raise ValueError("未能提取到足够的正文内容")
                
                logger.info(f"Successfully fetched: {url}, title: {title[:50]}, content length: {len(content)}")
                return title, content
                
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching URL: {url}")
            raise ValueError("网页加载超时，请稍后重试或直接粘贴文本")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching URL {url}: {e}")
            raise ValueError(f"网络请求失败: {str(e)}")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            raise ValueError(f"抓取失败: {str(e)}")
    
    def _extract_content(self, html: str) -> Tuple[str, str]:
        """
        从 HTML 提取标题和正文
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # 提取标题
        title = self._extract_title(soup)
        
        # 移除不需要的标签
        for tag_name in self.REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # 尝试找到主要内容区域
        content = self._extract_main_content(soup)
        
        # 清理文本
        content = self._clean_text(content)
        
        return title, content
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        # 优先使用 og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        
        # 其次使用 <title>
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # 最后使用 h1
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取主要正文内容"""
        # 尝试常见的内容容器
        content_selectors = [
            "article",
            "[role='main']",
            ".post-content",
            ".article-content",
            ".entry-content",
            ".content",
            ".post",
            ".article",
            "main",
            "#content",
            "#main",
        ]
        
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                text = content_area.get_text(separator="\n", strip=True)
                if len(text) > 200:  # 确保有足够内容
                    return text
        
        # 如果没找到特定容器，提取 body 中的所有段落
        paragraphs = soup.find_all("p")
        if paragraphs:
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
            if text:
                return text
        
        # 最后回退到 body
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """清理提取的文本"""
        # 移除多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # 移除常见的网站元素文本
        noise_patterns = [
            r'Subscribe.*newsletter',
            r'Sign up.*free',
            r'Click here.*',
            r'Read more.*',
            r'Share this.*',
            r'Follow us.*',
            r'Copyright.*',
            r'All rights reserved.*',
            r'Cookie.*policy',
            r'Privacy.*policy',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 限制长度
        if len(text) > 10000:
            text = text[:10000]
            # 在句子边界截断
            last_period = text.rfind('.')
            if last_period > 8000:
                text = text[:last_period + 1]
        
        return text.strip()


# 创建服务实例
scraper_service = ScraperService()
