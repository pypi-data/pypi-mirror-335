# -*- coding: utf-8 -*-
"""
作者: Python_Xueba
日期: 2025/3/23
"""
import libtorrent as lt
import time
import urllib.parse
import requests
import os
import sys
import select
import argparse
from colorama import init, Fore, Style
import logging

# 初始化 colorama 以支持跨平台彩色输出
init(autoreset=True)

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DownloadManager:
    def __init__(self):
        """初始化下载管理器"""
        self.session = None
        self.tracker_index = 0  # 当前使用的 Tracker 索引
        self.original_trackers = []  # 自带 Tracker 列表
        self.backup_trackers = self._fetch_trackers()  # 预备 Tracker 列表
        self.all_trackers = []  # 合并后的 Tracker 列表（优先使用自带，后接预备）
        os.makedirs("./downloads", exist_ok=True)  # 创建下载目录
        self.backup_dht_nodes = self._fetch_dht_nodes()  # 预备 DHT 节点
        self._init_session()  # 初始化 libtorrent 会话

    def _fetch_trackers(self):
        """从网络获取预备 Tracker 列表，失败时使用默认列表"""
        try:
            response = requests.get("https://trackers.run/s/wp_hp_hs_v4_v6.txt", timeout=10)
            if response.status_code == 200:
                trackers = [t.strip() for t in response.text.split('\n') if t.strip()]
                print(f"{Fore.GREEN}✓ 已加载 {len(trackers)} 个预备 Tracker{Style.RESET_ALL}")
                return trackers
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ 获取预备 Tracker 失败: {e}，使用默认列表{Style.RESET_ALL}")
        return [
            "udp://tracker.opentrackr.org:1337/announce",
            "udp://tracker.openbittorrent.com:6969/announce",
            "udp://exodus.desync.com:6969/announce",
            "udp://tracker.torrent.eu.org:451/announce",
            "udp://open.stealth.si:80/announce",
            "http://tracker.files.fm:6969/announce",
        ]

    def _fetch_dht_nodes(self):
        """提供预备 DHT 节点列表"""
        nodes = [
            ("router.bittorrent.com", 6881),
            ("router.utorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.libtorrent.org", 25401),
            ("dht.aelitis.com", 6881),
            ("router.bitcomet.com", 6881),
        ]
        print(f"{Fore.GREEN}✓ 已加载 {len(nodes)} 个预备 DHT 节点{Style.RESET_ALL}")
        return nodes

    def _init_session(self):
        """初始化 libtorrent 下载设置"""
        self.session = lt.session({
            'download_rate_limit': 0,
            'upload_rate_limit': 25 * 1024 * 1024,  # 上传速度
            'active_downloads': 16,  # 活动下载数
            'active_seeds': 10,  # 活动种子数
            'connections_limit': 2000,  # 连接限制
            'connection_speed': 400,
            'enable_dht': True,
            'enable_lsd': True,
            'enable_upnp': True,
            'enable_natpmp': True,
            'announce_to_all_tiers': True,
            'announce_to_all_trackers': True,
            'aio_threads': 32,  # 异步I/O线程数
            'cache_size': 262144,  # 缓存大小
        })
        for host, port in self.backup_dht_nodes:
            try:
                self.session.add_dht_node((host, port))
            except Exception as e:
                logging.warning(f"添加 DHT 节点 {host}:{port} 失败: {e}")
        for ext in ['ut_metadata', 'ut_pex', 'smart_ban']:
            self.session.add_extension(ext)

    def _switch_tracker(self, handle, manual=False):
        """切换到下一个可用 Tracker 并返回切换后的状态"""
        if not self.all_trackers:
            print(f"{Fore.YELLOW}⚠ 无可用 Tracker{Style.RESET_ALL}")
            return None
        attempts = 0
        while attempts < len(self.all_trackers):
            self.tracker_index = (self.tracker_index + 1) % len(self.all_trackers)
            new_tracker = self.all_trackers[self.tracker_index]
            try:
                response = requests.get(new_tracker, timeout=5)
                if response.status_code in (200, 301, 302):
                    break
                else:
                    print(f"{Fore.YELLOW}⚠ Tracker {new_tracker} 响应异常，尝试下一个{Style.RESET_ALL}")
            except requests.RequestException:
                print(f"{Fore.YELLOW}⚠ Tracker {new_tracker} 不可用，尝试下一个{Style.RESET_ALL}")
            attempts += 1
        if attempts >= len(self.all_trackers):
            print(f"{Fore.YELLOW}⚠ 所有 Tracker 均不可用{Style.RESET_ALL}")
            return None

        logging.info(f"{'手动' if manual else '自动'}切换 Tracker: {new_tracker}")
        print(f"\n{Fore.YELLOW}➤ {'手动' if manual else '自动'}切换 Tracker: {new_tracker}{Style.RESET_ALL}")
        handle.replace_trackers([lt.announce_entry(new_tracker)])
        handle.force_reannounce()
        handle.force_dht_announce()
        time.sleep(1)  # 等待连接更新
        status = handle.status()
        print(f"{Fore.YELLOW}切换后状态: Peers: {status.num_peers}, Seeds: {status.num_seeds}, Speed: {self._human_readable_size(status.download_rate, 1)}/s{Style.RESET_ALL}")
        return status

    def parse_magnet_link(self, magnet_link):
        """解析磁力链接，优先使用自带 Tracker，无自带 Tracker 时使用预备资源"""
        magnet_link = magnet_link.strip()
        if not magnet_link.startswith("magnet:?"):
            if len(magnet_link) in (32, 40) and all(c in "0123456789abcdefABCDEF" for c in magnet_link):
                magnet_link = f"magnet:?xt=urn:btih:{magnet_link}"
            else:
                raise ValueError("无效的磁力链接或哈希值")

        # 解析原始参数
        parsed_url = urllib.parse.urlsplit(magnet_link)
        params = urllib.parse.parse_qs(parsed_url.query)
        xt = params.get('xt', [''])[0]
        if not xt.startswith('urn:btih:'):
            raise ValueError("无法识别 InfoHash")

        info_hash = xt.replace('urn:btih:', '')
        print(f"{Fore.YELLOW}调试: 提取到的 InfoHash: {info_hash}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}调试: 原始磁力链接: {magnet_link}{Style.RESET_ALL}")

        if len(info_hash) not in (32, 40):
            raise ValueError("InfoHash 长度无效，必须为 32 或 40 位")

        display_name = urllib.parse.unquote_plus(params.get('dn', [''])[0]) if params.get('dn') else None
        self.original_trackers = [urllib.parse.unquote(tr) for tr in params.get('tr', []) if tr]
        file_size = int(params.get('xl', ['0'])[0]) if params.get('xl') else None

        # 优先使用自带 Tracker，之后追加预备 Tracker
        self.all_trackers = list(dict.fromkeys(self.original_trackers + self.backup_trackers))  # 去除重复并保持顺序
        print(f"{Fore.YELLOW}调试: 自带 Tracker 数量: {len(self.original_trackers)}{Style.RESET_ALL}")
        if self.original_trackers:
            print(f"{Fore.YELLOW}调试: 自带 Tracker: {self.original_trackers}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}调试: 无自带 Tracker，使用预备资源{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}调试: 预备 Tracker 数量: {len(self.backup_trackers)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}调试: 总 Tracker 数量: {len(self.all_trackers)}{Style.RESET_ALL}")

        effective_magnet = magnet_link
        if not self.original_trackers:
            enhanced_magnet = f"magnet:?xt=urn:btih:{info_hash}"
            if display_name:
                enhanced_magnet += f"&dn={urllib.parse.quote_plus(display_name)}"
            if file_size:
                enhanced_magnet += f"&xl={file_size}"
            for tracker in self.backup_trackers:
                enhanced_magnet += f"&tr={urllib.parse.quote(tracker)}"
            effective_magnet = enhanced_magnet
            print(f"{Fore.YELLOW}调试: 增强后的磁力链接: {effective_magnet}{Style.RESET_ALL}")

        atp = lt.add_torrent_params()
        atp.url = effective_magnet
        atp.flags |= lt.torrent_flags.update_subscribe | lt.torrent_flags.auto_managed
        atp.save_path = "./downloads"
        atp.max_connections = 300
        handle = self.session.add_torrent(atp)

        print(f"{Fore.CYAN}➤ 获取元数据 [{info_hash[:8]}...]{Style.RESET_ALL}", end="")
        start_time = time.time()
        retry_count = 0
        try:
            while not handle.status().has_metadata:
                elapsed = time.time() - start_time
                if elapsed > 120:
                    self.session.remove_torrent(handle)
                    raise TimeoutError("元数据获取超时")
                if retry_count < 2 and elapsed > 20 * (retry_count + 1):
                    print(f"\n{Fore.YELLOW}⚠ 获取缓慢，尝试优化连接...{Style.RESET_ALL}")
                    handle.force_reannounce()
                    handle.force_dht_announce()
                    retry_count += 1
                print(".", end="", flush=True)
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠ 用户中断元数据获取{Style.RESET_ALL}")
            self.session.remove_torrent(handle)
            raise

        torrent_info = handle.torrent_file()
        files = [{'path': torrent_info.files().file_path(i), 'size': torrent_info.files().file_size(i), 'index': i}
                 for i in range(torrent_info.num_files())]
        self.session.remove_torrent(handle)
        print(f"\n{Fore.GREEN}✓ 元数据获取成功{Style.RESET_ALL}")

        return {
            'info_hash': info_hash,
            'name': display_name or torrent_info.name(),
            'total_size': torrent_info.total_size(),
            'total_size_human': self._human_readable_size(torrent_info.total_size()),
            'files': files,
            'effective_magnet': effective_magnet,
            'original_trackers': self.original_trackers
        }

    def download_torrent(self, magnet_link, selected_files=None):
        """下载磁力链接种子，优先使用自带 Tracker"""
        atp = lt.add_torrent_params()
        atp.url = magnet_link
        atp.save_path = "./downloads"
        atp.flags |= lt.torrent_flags.auto_managed | lt.torrent_flags.update_subscribe
        atp.max_connections = 300
        handle = self.session.add_torrent(atp)

        # 优先使用自带 Tracker，从索引 0 开始
        if self.all_trackers:
            self.tracker_index = 0  # 重置为第一个 Tracker（自带 Tracker 的开头）
            handle.replace_trackers([lt.announce_entry(self.all_trackers[self.tracker_index])])
            print(f"{Fore.YELLOW}➤ 初始化使用 Tracker: {self.all_trackers[self.tracker_index]}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}➤ 正在获取元数据...{Style.RESET_ALL}")
        start_time = time.time()
        retry_count = 0
        try:
            while not handle.status().has_metadata:
                elapsed = time.time() - start_time
                if elapsed > 120:
                    self.session.remove_torrent(handle)
                    raise TimeoutError("元数据获取超时")
                if retry_count < 2 and elapsed > 20 * (retry_count + 1):
                    print(f"\n{Fore.YELLOW}⚠ 获取缓慢，尝试优化连接...{Style.RESET_ALL}")
                    handle.force_reannounce()
                    handle.force_dht_announce()
                    retry_count += 1
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠ 用户中断下载{Style.RESET_ALL}")
            self.session.remove_torrent(handle)
            return

        torrent_info = handle.torrent_file()
        total_size = torrent_info.total_size()

        if selected_files:
            file_priorities = [0] * torrent_info.num_files()
            for idx in selected_files:
                if 0 <= idx < torrent_info.num_files():
                    file_priorities[idx] = 7
            handle.prioritize_files(file_priorities)
            selected_size = sum(torrent_info.files().file_size(i) for i in selected_files
                                if 0 <= i < torrent_info.num_files())
            print(f"{Fore.GREEN}✓ 下载 {len(selected_files)} 个文件 [{self._human_readable_size(selected_size)}]{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ 下载全部 [{self._human_readable_size(total_size)}]{Style.RESET_ALL}")

        handle.set_download_limit(0)
        handle.set_upload_limit(0)
        piece_count = torrent_info.num_pieces()
        if piece_count > 0:
            for i in range(piece_count):
                handle.piece_priority(i, 4)
            for i in range(min(100, piece_count)):
                handle.piece_priority(i, 7)
            for i in range(max(0, piece_count - 100), piece_count):
                handle.piece_priority(i, 7)

        last_progress = 0
        slow_start_time = None
        start_time = time.time()

        print(f"{Fore.CYAN}➤ 输入 'x' 手动切换 Tracker，输入 'q' 退出{Style.RESET_ALL}")
        while True:
            status = handle.status()
            progress = status.progress * 100
            if progress >= 100 or str(status.state) == "seeding":
                print(f"\n{Fore.GREEN}✓ 下载完成: {atp.save_path}/{torrent_info.name()}{Style.RESET_ALL}")
                self.session.remove_torrent(handle)
                break

            term_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
            bar_length = max(20, term_width // 3)
            filled = int(progress / 100 * bar_length)
            bar = '█' * filled + '░' * (bar_length - filled)
            download_rate = self._human_readable_size(status.download_rate, 1)
            upload_rate = self._human_readable_size(status.upload_rate, 1)
            downloaded = self._human_readable_size(status.total_done, 1)
            total = self._human_readable_size(total_size, 1)
            eta = self._calculate_eta(status.download_rate, total_size - status.total_done)

            status_line = (
                f"\r{Fore.CYAN}进度:{Style.RESET_ALL} [{Fore.GREEN}{bar}{Style.RESET_ALL}] {progress:.1f}% "
                f"↓ {Fore.GREEN if status.download_rate > 50000 else Fore.YELLOW}{download_rate}/s{Style.RESET_ALL} "
                f"↑ {upload_rate}/s P:{status.num_peers} S:{status.num_seeds} [{downloaded}/{total}] ETA:{eta}"
            )
            sys.stdout.write(status_line[:term_width - 1] + " ")
            sys.stdout.flush()

            if status.download_rate < 102400 and progress > 0 and progress < 99:
                if slow_start_time is None:
                    slow_start_time = time.time()
                elif time.time() - slow_start_time >= 10:
                    print(f"\n{Fore.YELLOW}⚠ 下载速度低于 100KB/s 超过 10 秒，切换 Tracker{Style.RESET_ALL}")
                    self._switch_tracker(handle)
                    slow_start_time = None
            else:
                slow_start_time = None

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip().lower()
                if line == 'x':
                    self._switch_tracker(handle, manual=True)
                elif line == 'q':
                    print(f"\n{Fore.YELLOW}⚠ 用户退出下载{Style.RESET_ALL}")
                    self.session.remove_torrent(handle)
                    break

            if abs(progress - last_progress) < 0.1 and progress < 99 and time.time() - start_time > 60:
                print(f"\n{Fore.YELLOW}⚠ 下载卡住，重新连接...{Style.RESET_ALL}")
                handle.force_reannounce()
                handle.force_dht_announce()
                start_time = time.time()
            last_progress = progress
            time.sleep(0.5)

    def download_file(self, url):
        """下载非磁力文件（HTTP/HTTPS/FTP 等直链）"""
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            filename = os.path.basename(urllib.parse.urlparse(url).path) or "downloaded_file"
            filepath = os.path.join("./downloads", filename)

            print(f"{Fore.CYAN}➤ 下载文件: {filename} [{self._human_readable_size(total_size)}]{Style.RESET_ALL}")
            downloaded = 0
            start_time = time.time()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size * 100
                            eta = self._calculate_eta(downloaded / (time.time() - start_time), total_size - downloaded)
                            term_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
                            bar_length = max(20, term_width // 3)
                            filled = int(progress / 100 * bar_length)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            status_line = (
                                f"\r{Fore.CYAN}进度:{Style.RESET_ALL} [{Fore.GREEN}{bar}{Style.RESET_ALL}] {progress:.1f}% "
                                f"[{self._human_readable_size(downloaded)}/{self._human_readable_size(total_size)}] ETA:{eta}"
                            )
                            sys.stdout.write(status_line[:term_width - 1] + " ")
                            sys.stdout.flush()

            print(f"\n{Fore.GREEN}✓ 下载完成: {filepath}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ 下载失败: {e}{Style.RESET_ALL}")

    def _human_readable_size(self, size, decimal_places=2):
        """将字节大小转换为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f}{unit}"
            size /= 1024.0

    def _calculate_eta(self, rate, remaining):
        """计算预计完成时间"""
        if rate <= 0:
            return "∞"
        seconds = int(remaining / rate)
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m{(seconds % 60):02d}s"
        hours = minutes // 60
        return f"{hours}h{(minutes % 60):02d}m"

    def show_magnet_styles(self):
        """展示常见的磁力链接样式及其解析方式"""
        print(f"{Fore.CYAN}➤ 常见的磁力链接样式示例:{Style.RESET_ALL}")
        styles = [
            {
                "description": "完整格式（带 Tracker、名称、大小）",
                "example": "magnet:?xt=urn:btih:XBBQH2NQQCX2RUF6OFW7IHIXLLWPB5GE&dn=Example&tr=udp://tracker.opentrackr.org:1337/announce&xl=420456835",
                "parsed": "InfoHash: XBBQH2NQQCX2RUF6OFW7IHIXLLWPB5GE, Name: Example, Tracker: udp://tracker.opentrackr.org:1337/announce, Size: 420456835"
            },
            {
                "description": "简短格式（仅 InfoHash 和 Tracker）",
                "example": "magnet:?xt=urn:btih:1234567890ABCDEF1234567890ABCDEF12345678&tr=udp://tracker.openbittorrent.com:6969",
                "parsed": "InfoHash: 1234567890ABCDEF1234567890ABCDEF12345678, Tracker: udp://tracker.openbittorrent.com:6969"
            },
            {
                "description": "极简格式（仅 InfoHash）",
                "example": "magnet:?xt=urn:btih:ABCDEF1234567890ABCDEF1234567890ABCDEF12",
                "parsed": "InfoHash: ABCDEF1234567890ABCDEF1234567890ABCDEF12"
            },
            {
                "description": "纯 InfoHash（非标准，自动补全）",
                "example": "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
                "parsed": "InfoHash: ABCDEF1234567890ABCDEF1234567890ABCDEF12 (自动转为 magnet:?xt=urn:btih:...)"
            }
        ]
        for style in styles:
            print(f"{Fore.GREEN}样式: {style['description']}{Style.RESET_ALL}")
            print(f"  示例: {style['example']}")
            print(f"  解析: {style['parsed']}\n")

def parse_indices(input_str, max_index):
    """解析用户输入的文件索引"""
    selected_indices = set()
    for part in input_str.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                selected_indices.update(range(max(start, 0), min(end + 1, max_index + 1)))
            except ValueError:
                print(f"{Fore.YELLOW}⚠ 无效范围 '{part}'{Style.RESET_ALL}")
        else:
            try:
                idx = int(part)
                if 0 <= idx <= max_index:
                    selected_indices.add(idx)
                else:
                    print(f"{Fore.YELLOW}⚠ 索引 {idx} 超出范围{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.YELLOW}⚠ 无效索引 '{part}'{Style.RESET_ALL}")
    return list(selected_indices)

def detect_link_type(url):
    """检测链接类型并返回建议操作"""
    if url.startswith("magnet:") or (len(url) in (32, 40) and all(c in "0123456789abcdefABCDEF" for c in url)):
        return "torrent", "磁力链接下载"
    elif url.startswith(("http://", "https://", "ftp://")):
        return "file", "直链文件下载"
    return "unknown", "未知类型"

def main():
    """主函数，处理命令行参数和交互模式"""
    parser = argparse.ArgumentParser(description="XB 下载器 - 支持磁力和直链")
    parser.add_argument("url", nargs="?", help="磁力链接或直链地址")
    parser.add_argument("--show-styles", action="store_true", help="展示磁力链接样式")
    args = parser.parse_args()

    print(f"{Fore.CYAN}╔════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║     XB Downloader                  ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚════════════════════════════════════╝{Style.RESET_ALL}")

    try:
        downloader = DownloadManager()
    except Exception as e:
        print(f"{Fore.RED}✗ 初始化失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

    if args.show_styles:
        downloader.show_magnet_styles()
        sys.exit(0)

    url = args.url
    interactive = not url

    while True:
        try:
            if not url:
                url = input(f"{Fore.CYAN}➤ 输入磁力链接或直链 (输入 'q' 退出, 'styles' 查看样式): {Style.RESET_ALL}").strip()
                if url.lower() == 'q':
                    break
                if url.lower() == 'styles':
                    downloader.show_magnet_styles()
                    url = None
                    continue
                if not url:
                    print(f"{Fore.YELLOW}⚠ 请输入有效的链接{Style.RESET_ALL}")
                    continue

            link_type, suggestion = detect_link_type(url)
            print(f"{Fore.CYAN}➤ 检测到类型: {suggestion}{Style.RESET_ALL}")

            if link_type == "torrent":
                parsed_info = downloader.parse_magnet_link(url)
                print(f"\n{Fore.GREEN}╔════ 种子信息 ════╗{Style.RESET_ALL}")
                print(f"{Fore.GREEN}║ 名称: {parsed_info['name'][:40]}{'...' if len(parsed_info['name']) > 40 else ''}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}║ 哈希: {parsed_info['info_hash'][:8]}...{Style.RESET_ALL}")
                print(f"{Fore.GREEN}║ 大小: {parsed_info['total_size_human']}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}╚═══════════════════╝{Style.RESET_ALL}")

                if len(parsed_info['files']) > 1 and interactive:
                    print(f"\n{Fore.CYAN}📁 文件列表:{Style.RESET_ALL}")
                    for i, file in enumerate(parsed_info['files']):
                        print(f"  [{Fore.YELLOW}{i}{Style.RESET_ALL}] {file['path'][:50]}{'...' if len(file['path']) > 50 else ''} [{downloader._human_readable_size(file['size'])}]")
                    choice = input(f"{Fore.CYAN}➤ 选择操作: (a)全部下载, (s)选择文件, (n)跳过: {Style.RESET_ALL}").lower()
                    if choice == 's':
                        indices_input = input(f"{Fore.CYAN}➤ 输入索引 (例如 0-2,4): {Style.RESET_ALL}")
                        selected_files = parse_indices(indices_input, len(parsed_info['files']) - 1)
                        if not selected_files:
                            print(f"{Fore.YELLOW}⚠ 未选择有效文件{Style.RESET_ALL}")
                            continue
                    elif choice == 'a':
                        selected_files = None
                    else:
                        url = None
                        continue
                else:
                    selected_files = None
                    if interactive and len(parsed_info['files']) > 1:
                        print(f"{Fore.YELLOW}⚠ 多个文件，默认下载全部{Style.RESET_ALL}")

                downloader.download_torrent(parsed_info['effective_magnet'], selected_files)

            elif link_type == "file":
                downloader.download_file(url)

            else:
                print(f"{Fore.YELLOW}⚠ 不支持的链接类型: {url}{Style.RESET_ALL}")
                continue

            if not interactive:
                break
            again = input(f"{Fore.CYAN}➤ 下载另一个文件? (y/n): {Style.RESET_ALL}").lower()
            if again != 'y':
                break
            url = None

        except (TimeoutError, ValueError) as e:
            print(f"{Fore.RED}✗ 错误: {e}{Style.RESET_ALL}")
            if not interactive:
                sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠ 用户中断程序{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}✗ 未知错误: {e}{Style.RESET_ALL}")
            if not interactive:
                sys.exit(1)

        if interactive:
            again = input(f"{Fore.CYAN}➤ 重试或新链接? (y/n): {Style.RESET_ALL}").lower()
            if again != 'y':
                break
            url = None

    print(f"{Fore.GREEN}✓ 感谢使用 XB 下载器!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()