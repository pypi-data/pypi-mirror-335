import json
import logging
import os
import requests
from urllib.parse import urlparse, urlunparse
from requests.exceptions import RequestException
from typing import Any, List, Optional
from pathlib import Path
from requests_toolbelt import MultipartEncoder
from tqdm import tqdm
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 预定义网关列表
_ODK_GATEWAYS = [
    "https://m.oldking.club",
    "https://cnodk.oldking.club",
    "https://pubodk.oldking.club",
    "https://video.oldking.club",
    "https://odkcfdb.oldking.club",
    "https://cdn.oldking.club",
]
CRUST_AUTH_TOKEN = "Bearer c3Vic3RyYXRlLWNUR2NoRGE3VktRUkg4clBiUTZ0MnZzaFhuWWp6bnZ5UmMxUHBjNG5aVDd3ODQ3ek46MHg3YWU5ZWE2NzEyNDhlYjA0ZjZiZTMwYWFkMGRmMTc4ODJlMzhlMzExOTY1MDZlZjEwMzUxYTYwZTA5ZTgyODYxNDc1ODBiYWJiYzYyMmZmOTQ5MjgwMWVlMWJmMzU3Njg5MjM3M2ZiMzRmNGUzZWE1ZjRkZTAzMDQwOTc1MGU4MQ=="
class DownloadError(Exception):
    """自定义下载异常"""
    pass

class SizeMismatchError(Exception):
    """内容长度不匹配异常"""
    pass

def _download_chunk(url: str, start: int, end: int, 
                   output: Path, session: requests.Session,
                   progress: tqdm) -> None:
    """下载文件分块（带进度更新）"""
    headers = {'Range': f'bytes={start}-{end}'}
    try:
        with session.get(url, headers=headers, stream=True, timeout=10) as response:
            response.raise_for_status()
            
            with open(output, 'r+b') as f:
                f.seek(start)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(len(chunk))  # 更新进度条
    except Exception as e:
        raise DownloadError(f"分块下载失败: {str(e)}")

def _download_file_with_retry(url: str, output: Path, threads: int = 4) -> None:
    print("下载文件:",url," -> ",output)
    """带进度显示的多线程下载文件"""
    try:
        with requests.Session() as session:
            # 获取文件元数据
            head = session.head(url, timeout=5)
            head.raise_for_status()
            
            if 'Content-Length' not in head.headers:
                raise RuntimeError("Missing Content-Length header")

            file_size = int(head.headers['Content-Length'])
            
            # 初始化目标文件
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, 'wb') as f:
                f.truncate(file_size)  # 预分配空间

            # 创建进度条
            with tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=output.name,
                ncols=100  # 进度条宽度
            ) as pbar:
                
                # 计算分块范围
                chunk_size = file_size // threads
                ranges = [
                    (i * chunk_size, (i+1)*chunk_size -1) 
                    for i in range(threads -1)
                ]
                ranges.append( (ranges[-1][1]+1, file_size-1) )

                # 启动下载线程
                workers = []
                for start, end in ranges:
                    t = threading.Thread(
                        target=_download_chunk,
                        args=(url, start, end, output, session, pbar)
                    )
                    t.start()
                    workers.append(t)

                # 等待所有线程完成
                for t in workers:
                    t.join()
                
    except RequestException as e:
        raise DownloadError(f"下载请求失败: {str(e)}")

def _try_single_gateway_with_len(gateway: str, url_path: str, file_path: str, expected_len: str) -> Optional[Exception]:
    """尝试单个网关下载"""
    try:
        # 构建完整URL
        parsed = urlparse(gateway)
        data_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            url_path, "", "", ""
        ))
        
        logger.info(f"尝试网关: {data_url}")
        
        # HEAD请求验证
        head_resp = requests.head(data_url, timeout=5)
        head_resp.raise_for_status()
        
        actual_len = head_resp.headers.get('Content-Length')
        if actual_len != expected_len:
            raise SizeMismatchError(
                f"内容长度不匹配，期望: {expected_len}，实际: {actual_len}"
            )
            
        # 开始下载
        output_path = Path(file_path)
        _download_file_with_retry(data_url, output_path)
        return None
    
    except SizeMismatchError as e:
        raise
        
    except Exception as e:
        logger.error(f"网关 {gateway} 失败: {str(e)}")
        return e


def _try_single_gateway(gateway: str, url_path: str, file_path: str, expected_len: str) -> Optional[Exception]:
    """尝试单个网关下载"""
    try:
        # 构建完整URL
        parsed = urlparse(gateway)
        data_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            url_path, "", "", ""
        ))
        
        logger.info(f"尝试网关: {data_url}")
        
        # HEAD请求验证
        head_resp = requests.head(data_url, timeout=5)
        head_resp.raise_for_status()
        
        # 开始下载
        output_path = Path(file_path)
        _download_file_with_retry(data_url, output_path)
        return None
        
    except Exception as e:
        logger.error(f"网关 {gateway} 失败: {str(e)}")
        return e


def odk_ipfs_download_with_len(
    url_path: str, 
    file_path: str, 
    content_length: str,
    gateways: List[str] = None
) -> None:
    """
    通过多个IPFS网关下载文件
    
    :param url_path: 资源路径 (e.g. /ipfs/Qm...)
    :param file_path: 本地保存路径
    :param content_length: 预期的Content-Length
    :param gateways: 可选自定义网关列表
    """
    gateways = gateways or _ODK_GATEWAYS
    
    for gateway in gateways:
        error = _try_single_gateway_with_len(gateway, url_path, file_path, content_length)
        if not error:
            logger.info(f"成功通过 {gateway} 下载到 {file_path}")
            return
    raise DownloadError("所有网关尝试失败")

def odk_ipfs_download(
    url_path: str, 
    file_path: str, 
    gateways: List[str] = None
) -> None:
    """
    通过多个IPFS网关下载文件
    
    :param url_path: 资源路径 (e.g. /ipfs/Qm...)
    :param file_path: 本地保存路径
    :param content_length: 预期的Content-Length
    :param gateways: 可选自定义网关列表
    """
    gateways = gateways or _ODK_GATEWAYS
    
    for gateway in gateways:
        error = _try_single_gateway(gateway, url_path, file_path)
        if not error:
            logger.info(f"成功通过 {gateway} 下载到 {file_path}")
            return
            
    raise DownloadError("所有网关尝试失败")

from threading import Event
import concurrent.futures
import time
from typing import Tuple, Optional

# 网关选择器
class GatewaySelector:
    def __init__(self, gateways: List[str], timeout: float = 5.0):
        self.gateways: List[str] = []
        self.timeout = timeout
        
        for gw in gateways:
            try:
                parsed = urlparse(gw)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError("Invalid URL structure")
                self.gateways.append(gw)
            except Exception as e:
                logging.warning(f"Invalid gateway {gw}: {str(e)}")

    def find_available_gateway(self, path: str) -> Optional[str]:
        available_event = Event()
        result = None
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.check_cid_availability, gw, path): gw
                for gw in self.gateways
            }
            
            try:
                # 优先返回第一个成功的响应
                for future in concurrent.futures.as_completed(
                    futures, timeout=self.timeout
                ):
                    if future.result():
                        result = futures[future]
                        available_event.set()
                        break
            except concurrent.futures.TimeoutError:
                logging.debug("Gateway selection timed out")
            except Exception as e:
                logging.error(f"Error during gateway selection: {str(e)}")

        return result
    def find_available_upload_gateway(self, path: str) -> Optional[str]:
            available_event = Event()
            result = None
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self.check_upload_availability, gw, path): gw
                    for gw in self.gateways
                }
                
                try:
                    # 优先返回第一个成功的响应
                    for future in concurrent.futures.as_completed(
                        futures, timeout=self.timeout
                    ):
                        if future.result():
                            result = futures[future]
                            available_event.set()
                            break
                except concurrent.futures.TimeoutError:
                    logging.debug("Gateway selection timed out")
                except Exception as e:
                    logging.error(f"Error during gateway selection: {str(e)}")

            return result

    def check_cid_availability(self, gateway: str, path: str) -> bool:
        full_url = f"{gateway.rstrip('/')}/{path.lstrip('/')}"
        # 配置请求头
        headers = {
            "Authorization": CRUST_AUTH_TOKEN,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Origin": "https://crustfiles.io",
            "Referer": "https://crustfiles.io",
            "Accept-Encoding": "gzip, deflate, br"
        }
        try:
            # 使用流模式避免下载完整内容
            response = requests.head(
                full_url,
                timeout=2,
                allow_redirects=False,
                headers=headers
            )
            
            # 检查 2xx 和 3xx 状态码（根据需求调整）
            return 200 <= response.status_code < 400
            
        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
            logging.debug(f"Gateway {gateway} unavailable: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error checking {gateway}: {str(e)}")
            return False
    def check_upload_availability(self, gateway: str, path: str) -> bool:
        full_url = f"{gateway.rstrip('/')}/{path.lstrip('/')}"
        # 配置请求头
        headers = {
            "Authorization": CRUST_AUTH_TOKEN,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Origin": "https://crustfiles.io",
            "Referer": "https://crustfiles.io",
            "Accept-Encoding": "gzip, deflate, br"
        }
        try:
            # 使用流模式避免下载完整内容
            response = requests.head(
                full_url,
                timeout=2,
                allow_redirects=False,
                headers=headers
            )
            
            # 检查 2xx 和 3xx 状态码（根据需求调整）
            return 200 <= response.status_code < 406
            
        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
            logging.debug(f"Gateway {gateway} unavailable: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error checking {gateway}: {str(e)}")
            return False
          
# 获取json数据 
def odk_ipfs_get_json(url_path: str) -> Tuple[Optional[Any],Optional[Exception]]:
    selector = GatewaySelector(_ODK_GATEWAYS)
    if available_gw := selector.find_available_gateway(url_path):
        print(f"Available gateway: {available_gw}")
        full_url = f"{available_gw.rstrip('/')}/{url_path.lstrip('/')}"
        try:
            response = requests.get(
                full_url,
                headers={"Accept": "application/json"},
                timeout=5
            )
            response.raise_for_status()
            # 验证内容类型
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                logger.warning(f"非JSON响应类型: {content_type}")
                return None, ValueError("Invalid content type")
            # 解析JSON
            try:
                return response.json(), None
            except ValueError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                return None, ValueError(f"Invalid JSON: {response.text[:200]}...")
        except requests.RequestException as e :
            return None, ConnectionError(f"Failed to fetch data: {str(e)}")
    else:
        return None, ConnectionError("No available gateways found")
    
# 全局变量增加缓存时间戳
_crust_upload_gateways = []
_crust_last_update = 0
_CACHE_TIMEOUT = 3600  # 缓存有效期1小时

# 获取上传列表
def odk_ipfs_get_crust_upload_gateways() -> Tuple[Optional[List[str]],Optional[Exception]]: 
    """
    获取Crust上传网关列表 (带缓存和验证)
    
    特性：
    - 全局缓存机制
    - 数据类型验证
    - 异常分类处理
    - 请求重试机制
    - 缓存过期控制
    """
    global _crust_upload_gateways, _crust_last_update
    
    # 检查缓存有效性
    if _crust_upload_gateways and time.time() - _crust_last_update < _CACHE_TIMEOUT:
        logger.debug("返回缓存的上传网关列表")
        return _crust_upload_gateways.copy(),None  # 返回副本防止意外修改
    
    # 获取网关数据
    crust_gateways , err = odk_ipfs_get_json("/ipns/crustendpoint.oldking.club")
    if err :
        return None,err 
    
    # 数据有效性验证
    if not isinstance(crust_gateways, dict):
        return None, ValueError("Invalid response format: expected dict")
        
    upload_gateways = crust_gateways.get("uploadgateways")
    if not isinstance(upload_gateways, list):
        return None, ValueError("uploadgateways field is not a list")
        
    if not all(isinstance(url, str) for url in upload_gateways):
        return None, ValueError("Invalid URL format in uploadgateways")
    
    # 更新缓存
    _crust_upload_gateways = upload_gateways
    _crust_last_update = time.time()
    logger.info(f"成功更新上传网关列表，共{len(upload_gateways)}个节点")
    return upload_gateways,None

# 上传文件到crust节点
def crust_upload_file_to_gateway(gateway: str, file_path: str) -> Tuple[Optional[str], Optional[Exception]]:
    """
    上传文件到Crust网关
    
    :param gateway: 网关地址 (e.g. "https://gw.crustfiles.net")
    :param file_path: 本地文件路径
    :return: (CID, 错误对象)
    """
    # 验证文件存在性
    if not os.path.exists(file_path):
        return None, FileNotFoundError(f"文件不存在: {file_path}")
    
    # 配置请求头
    headers = {
        "Authorization": CRUST_AUTH_TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Origin": "https://crustfiles.io",
        "Referer": "https://crustfiles.io",
        "Accept-Encoding": "gzip, deflate, br"
    }

    # 构造请求URL
    upload_url = f"{gateway.rstrip('/')}/api/v0/add?pin=true"
    try:
        # 打开文件并上传
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(
                upload_url,
                headers=headers,
                files=files,
                timeout=300  # 总超时300秒
            )

        # 检查HTTP状态码
        response.raise_for_status()

        # 解析JSON响应
        try:
            reply = response.json()
        except json.JSONDecodeError as e:
            return None, ValueError(f"无效的JSON响应: {response.text[:200]}")

        # 检查错误类型
        if reply.get('Type') == 'error':
            error_msg = reply.get('Message', '未知错误')
            return None, RuntimeError(f"网关返回错误: {error_msg}")

        # 获取CID
        cid = reply.get('Hash')
        if not cid:
            return None, KeyError("响应中缺少Hash字段")

        return cid, None

    except requests.exceptions.RequestException as e:
        # 细化网络错误类型
        error_type = "连接超时" if isinstance(e, requests.Timeout) else "网络错误"
        return None, ConnectionError(f"{error_type}: {str(e)}")
    except Exception as e:
        return None, e
    
# 通过Crust网关上传文件
def crust_upload_file(file_path: str) -> Tuple[Optional[str], Optional[Exception]]:
    upload_gateways ,err = odk_ipfs_get_crust_upload_gateways()
    if err:
        return None,err 
    selector = GatewaySelector(upload_gateways)
    if available_gw := selector.find_available_upload_gateway("/api/v0/add?pin=true"):
        return crust_upload_file_to_gateway(available_gw,file_path)
    else:
        return None,ConnectionError("No available gateways found")