# -*- coding: utf-8 -*-
"""
By Python_Xueba On 2025/3/23 
"""
import libtorrent as lt
import time
import re
import urllib.parse
import requests
import os
import sys
import random
import argparse
from colorama import init, Fore, Style

# 初始化colorama以支持跨平台彩色输出
init(autoreset=True)
class TorrentManager:
    def __init__(self):
        """初始化种子下载管理器"""
        self.session = None
        os.makedirs("./downloads", exist_ok=True)  # 创建下载目录
        self.trackers = self.get_trackers()  # 先初始化 trackers
        self.dht_nodes = self.get_dht_nodes()  # 先初始化 dht_nodes
        self.init_session()  # 然后调用 init_session

    def get_trackers(self):
        """从网络获取tracker列表，失败时使用默认扩展列表"""
        try:
            response = requests.get("https://cf.trackerslist.com/all.txt", timeout=10)
            if response.status_code == 200:
                trackers = [t.strip() for t in response.text.split('\n') if t.strip()]
                print(f"{Fore.GREEN}✓ 加载了 {len(trackers)} 个tracker{Style.RESET_ALL}")
                return trackers
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ 获取tracker失败: {e}，使用默认列表{Style.RESET_ALL}")
        return [
            "udp://tracker.opentrackr.org:1337/announce",
            "udp://tracker.openbittorrent.com:6969/announce",
            "udp://exodus.desync.com:6969/announce",
            "udp://tracker.torrent.eu.org:451/announce",
            "udp://open.stealth.si:80/announce",
            "udp://tracker.tiny-vps.com:6969/announce",
            "udp://p4p.arenabg.com:1337/announce",
            "udp://tracker.cyberia.is:6969/announce",
            "udp://tracker.moeking.me:6969/announce",
            "udp://opentracker.i2p.rocks:6969/announce",
            "udp://tracker.dler.org:6969/announce",
            "udp://tracker.birkenwald.de:6969/announce",
            "udp://tracker-udp.gbitt.info:80/announce",
            "udp://ipv4.tracker.harry.lu:80/announce",
            "udp://bt1.archive.org:6969/announce",
            "udp://bt2.archive.org:6969/announce",
            "http://tracker.files.fm:6969/announce",
            "http://tracker.gbitt.info:80/announce",
            "http://tracker.mywaifu.best:6969/announce",
            "http://tracker.bt4g.com:2095/announce",
            "http://open.acgnxtracker.com:80/announce"
        ]

    def get_dht_nodes(self):
        """提供扩展的DHT节点列表"""
        nodes = [
            ("router.bittorrent.com", 6881),
            ("router.utorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.libtorrent.org", 25401),
            ("dht.aelitis.com", 6881),
            ("router.bitcomet.com", 6881),
            ("dht.torkit.tk", 6881),
            ("dht.syndie.de", 6881),
            ("dht.kazi.to", 6881),
            ("dht.creativecow.net", 6881),
            ("router.bitcomet.net", 6881),
            ("dht.transmissionbt.org", 6881),
            ("bootstrap-dht.libtorrent.org", 6881),
            ("dht.tox.chat", 6881),
            ("dht.torkit.net", 6881),
            ("dht.bthub.eu", 6881),
            ("dht.bitspyder.net", 6881),
            ("router.dht.live", 6881),
            ("dht.istole.it", 6881),
            ("dht.sublimepeering.net", 6881),
            ("dht.thedutchbay.org", 6881),
            ("dht.trackerhub.net", 6881)
        ]
        print(f"{Fore.GREEN}✓ 加载了 {len(nodes)} 个DHT节点{Style.RESET_ALL}")
        return nodes

    def init_session(self):
        """初始化libtorrent会话并优化下载设置"""
        self.session = lt.session({
            'download_rate_limit': 0, 'upload_rate_limit': 20*1024*1024,
            'active_downloads': 8, 'active_seeds': 5, 'active_limit': 15,
            'connections_limit': 1000, 'connection_speed': 400,
            'allow_multiple_connections_per_ip': True, 'enable_dht': True,
            'enable_lsd': True, 'enable_upnp': True, 'enable_natpmp': True,
            'announce_to_all_tiers': True, 'announce_to_all_trackers': True,
            'aio_threads': 16, 'cache_size': 131072, 'mixed_mode_algorithm': 1,
            'seed_choking_algorithm': 1, 'request_timeout': 5, 'peer_timeout': 10,
            'max_peerlist_size': 3000, 'max_out_request_queue': 1500,
            'handshake_timeout': 10, 'dht_upload_rate_limit': 30000,
            'torrent_connect_boost': 80
        })
        for host, port in self.dht_nodes:
            try:
                self.session.add_dht_node((host, port))
            except Exception:
                pass  # 静默跳过失败的节点
        for ext in ['ut_metadata', 'ut_pex', 'smart_ban']:
            self.session.add_extension(ext)

    def parse_magnet_link(self, magnet_link):
        """解析并增强磁力链接"""
        if not magnet_link.startswith("magnet:?"):
            if re.match(r'^[a-fA-F0-9]{32,40}$', magnet_link):
                magnet_link = f"magnet:?xt=urn:btih:{magnet_link}"
            else:
                raise ValueError("无效的磁力链接或哈希值")
        info_hash_match = re.search(r'btih:([a-fA-F0-9]{32,40})', magnet_link, re.IGNORECASE)
        if not info_hash_match:
            raise ValueError("无法提取InfoHash")
        info_hash = info_hash_match.group(1).lower()
        params = dict(urllib.parse.parse_qsl(magnet_link.split('?')[1]))
        display_name = urllib.parse.unquote_plus(params.get('dn', '')) if params.get('dn') else None
        original_trackers = [urllib.parse.unquote(match.group(1)) for match in 
                            re.compile(r'tr(?:\d+)?=([^&]+)').finditer(magnet_link)]
        enhanced_magnet = f"magnet:?xt=urn:btih:{info_hash}"
        if display_name:
            enhanced_magnet += f"&dn={urllib.parse.quote_plus(display_name)}"
        all_trackers = list(set(original_trackers or self.trackers))
        for tracker in all_trackers:
            enhanced_magnet += f"&tr={urllib.parse.quote(tracker)}"
        
        atp = lt.add_torrent_params()
        atp.url = enhanced_magnet
        atp.flags |= lt.torrent_flags.update_subscribe | lt.torrent_flags.auto_managed
        atp.save_path = "./downloads"
        atp.max_connections = 300
        handle = self.session.add_torrent(atp)
        print(f"{Fore.CYAN}➤ 获取元数据 [{info_hash[:8]}...]{Style.RESET_ALL}", end="")
        start_time = time.time()
        while not handle.status().has_metadata:
            if time.time() - start_time > 30:
                self.session.remove_torrent(handle)
                raise TimeoutError("元数据获取超时")
            print(".", end="", flush=True)
            time.sleep(0.5)
        torrent_info = handle.torrent_file()
        files = [{'path': torrent_info.files().file_path(i), 'size': torrent_info.files().file_size(i), 'index': i} 
                 for i in range(torrent_info.num_files())]
        self.session.remove_torrent(handle)
        print(f"\n{Fore.GREEN}✓ 元数据获取成功{Style.RESET_ALL}")
        return {
            'info_hash': info_hash, 'name': display_name or torrent_info.name(),
            'total_size': torrent_info.total_size(), 'total_size_human': self._human_readable_size(torrent_info.total_size()),
            'files': files, 'enhanced_magnet': enhanced_magnet, 'original_trackers': original_trackers
        }

    def download_torrent(self, magnet_link, selected_files=None):
        """下载种子并优化速度与显示"""
        atp = lt.add_torrent_params()
        atp.url = magnet_link
        atp.save_path = "./downloads"
        atp.flags |= lt.torrent_flags.auto_managed | lt.torrent_flags.update_subscribe
        atp.max_connections = 300
        handle = self.session.add_torrent(atp)
        print(f"{Fore.CYAN}➤ 正在获取元数据...{Style.RESET_ALL}")
        start_time = time.time()
        while not handle.status().has_metadata:
            if time.time() - start_time > 30:
                self.session.remove_torrent(handle)
                raise TimeoutError("元数据获取超时")
            time.sleep(0.5)
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
            for i in range(min(50, piece_count)):
                handle.piece_priority(i, 7)
            for i in range(max(0, piece_count - 50), piece_count):
                handle.piece_priority(i, 7)
        last_progress = 0
        low_speed_count = 0
        start_time = time.time()
        while True:
            status = handle.status()
            progress = status.progress * 100
            if progress >= 100 or str(status.state) == "seeding":
                print(f"\n{Fore.GREEN}✓ 下载完成: {atp.save_path}/{torrent_info.name()}{Style.RESET_ALL}")
                self.session.remove_torrent(handle, lt.options_t.delete_files)
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
            sys.stdout.write(status_line[:term_width-1] + " ")
            sys.stdout.flush()
            if status.download_rate < 20000 and progress > 0 and progress < 99:
                low_speed_count += 1
                if low_speed_count >= 3:
                    print(f"\n{Fore.YELLOW}⚠ 下载速度慢 [{download_rate}/s]，优化中...{Style.RESET_ALL}")
                    handle.force_reannounce()
                    handle.force_dht_announce()
                    low_speed_count = 0
            else:
                low_speed_count = 0
            if abs(progress - last_progress) < 0.1 and progress < 99 and time.time() - start_time > 60:
                print(f"\n{Fore.YELLOW}⚠ 下载卡住，重新连接...{Style.RESET_ALL}")
                handle.force_reannounce()
                handle.force_dht_announce()
                start_time = time.time()
            last_progress = progress
            time.sleep(0.3)

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

def main():
    parser = argparse.ArgumentParser(description="XB Torrent Downloader")
    parser.add_argument("magnet", nargs="?", help="磁力链接")
    args = parser.parse_args()

    default_magnet = "no-default-magnet"
    
    print(f"{Fore.CYAN}╔════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║     XB Torrent Downloader          ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚════════════════════════════════════╝{Style.RESET_ALL}")

    try:
        torrent_mgr = TorrentManager()
    except Exception as e:
        print(f"{Fore.RED}✗ 初始化失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

    magnet_link = args.magnet
    interactive = not magnet_link

    while True:
        try:
            if not magnet_link:
                magnet_link = input(f"{Fore.CYAN}➤ 输入磁力链接 : {Style.RESET_ALL}").strip() or default_magnet
            
            parsed_info = torrent_mgr.parse_magnet_link(magnet_link)
            print(f"\n{Fore.GREEN}╔════ 种子信息 ════╗{Style.RESET_ALL}")
            print(f"{Fore.GREEN}║ 名称: {parsed_info['name'][:40]}{'...' if len(parsed_info['name']) > 40 else ''}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}║ 哈希: {parsed_info['info_hash'][:8]}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}║ 大小: {parsed_info['total_size_human']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}╚═══════════════════╝{Style.RESET_ALL}")

            if len(parsed_info['files']) > 1 and interactive:
                print(f"\n{Fore.CYAN}📁 文件列表:{Style.RESET_ALL}")
                for i, file in enumerate(parsed_info['files']):
                    print(f"  [{Fore.YELLOW}{i}{Style.RESET_ALL}] {file['path'][:50]}{'...' if len(file['path']) > 50 else ''} [{torrent_mgr._human_readable_size(file['size'])}]")
                choice = input(f"{Fore.CYAN}➤ (a)全部, (s)选择, (n)下一个: {Style.RESET_ALL}").lower()
                if choice == 's':
                    indices_input = input(f"{Fore.CYAN}➤ 输入索引 (例如 0-2,4): {Style.RESET_ALL}")
                    selected_files = parse_indices(indices_input, len(parsed_info['files']) - 1)
                    if not selected_files:
                        print(f"{Fore.YELLOW}⚠ 未选择有效文件{Style.RESET_ALL}")
                        continue
                elif choice == 'a':
                    selected_files = None
                else:
                    magnet_link = None
                    continue
            else:
                selected_files = None
                if interactive and len(parsed_info['files']) > 1:
                    print(f"{Fore.YELLOW}⚠ 多个文件，默认下载全部{Style.RESET_ALL}")

            torrent_mgr.download_torrent(parsed_info['enhanced_magnet'], selected_files)

            if not interactive:
                break
            again = input(f"{Fore.CYAN}➤ 下载另一个种子? (y/n): {Style.RESET_ALL}").lower()
            if again != 'y':
                break
            magnet_link = None

        except (TimeoutError, ValueError) as e:
            print(f"{Fore.RED}✗ 错误: {e}{Style.RESET_ALL}")
            if not interactive:
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}✗ 未知错误: {e}{Style.RESET_ALL}")
            if not interactive:
                sys.exit(1)

        if interactive:
            again = input(f"{Fore.CYAN}➤ 重试或新链接? (y/n): {Style.RESET_ALL}").lower()
            if again != 'y':
                break
            magnet_link = None

    print(f"{Fore.GREEN}✓ 感谢使用XB下载器!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()