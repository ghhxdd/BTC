import time
import random
import secp256k1 as ice
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from ranges import ranges
from os import system, name
from datetime import datetime
from rich.console import Console
from deep import sub_ranges
import requests
import multiprocessing as mp
import os
from functools import partial
import sys
import numpy as np
import gmpy2

version = "1.2.1"

maxcpucount = os.cpu_count()

console = Console()
current_priv_key = 0x10000000000000000000000000000000
current_range_index = 0
selected_range = None
current_sub_range_index = 0
current_sub_range = None


tg_token = "6379444172:AAG32TaA2m89nhj3DmVs8nGBbQAAuPK2YI4" #token BotFanter #https://crypto.oni.su/10-kak-sozdat-telegramm-bota-v-botfather.html
tg_id = "610531310" #id Get My ID

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/, %H:%M:%S")

def send_telegram(message, chat_id, token):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=payload)
    return response.ok

def cls():
    system('cls' if name=='nt' else 'clear')

def convert_int(num: int):
    dict_suffix = {0: 'key', 1: 'Kkey', 2: 'Mkey', 3: 'Gkey', 4: 'Tkey', 5: 'Pkey', 6: 'Ekeys'}
    num *= 1.0
    idx = 0
    for ii in range(len(dict_suffix) - 1):
        if int(num / 1000) > 0:
            idx += 1
            num /= 1000
        else:
            break
    return f"{num:.2f}", dict_suffix[idx]

def get_compressed_pubkey(priv_key_hex):
    private_key = int(priv_key_hex, 16)
    public_key = ice.scalar_multiplication(private_key)
    compressed_public_key = ice.point_to_cpub(public_key)
    return compressed_public_key

def get_compressed_address(priv_key_hex):
    private_key = int(priv_key_hex, 16)
    address = ice.privatekey_to_address(0, True, private_key)
    return address

def divide_subrange(sub_range, num_threads):
    start = int(sub_range[0], 16)
    end = int(sub_range[1], 16)
    step = (end - start) // num_threads

    divided_subranges = []
    for i in range(num_threads):
        subrange_start = start + i * step
        subrange_end = start + (i + 1) * step - 1 if i < num_threads - 1 else end
        divided_subranges.append((f"{subrange_start:064x}", f"{subrange_end:064x}"))

    return divided_subranges

def cls():
    system('cls' if name=='nt' else 'clear')

def convert_int(num: int):
    dict_suffix = {0: 'key', 1: 'Kkey', 2: 'Mkey', 3: 'Gkey', 4: 'Tkey', 5: 'Pkey', 6: 'Ekeys', 7: 'Zkey', 8: 'Ykey'}
    num *= 1.0
    idx = 0
    for ii in range(len(dict_suffix) - 1):
        if int(num / 1000) > 0:
            idx += 1
            num /= 1000
        else:
            break
    return f"{num:.2f}", dict_suffix[idx]

random_generator = random.Random(42)
def full_sequential_subrange(selected_range, range_index, num_threads):
    global current_priv_key
    global current_sub_range_index
    global current_sub_range

    # Определите thread_id, используя текущий процесс
    thread_id = multiprocessing.current_process().name.split('-')[-1]
    thread_id = int(thread_id) % num_threads

    if current_sub_range is None or current_priv_key >= int(current_sub_range[1], 16):
        sub_ranges_list = sub_ranges[range_index]
        divided_sub_ranges = [sub_ranges_list[i::num_threads] for i in range(num_threads)]
        
        if not divided_sub_ranges[thread_id]:  # Если список пустой, завершить работу функции
            return None

        current_sub_range = random_generator.choice(divided_sub_ranges[thread_id])  # выбираем случайный поддиапазон из списка
        current_priv_key = int(str(current_sub_range[0]), 16)
        #print(f"Switching to subrange: {current_sub_range[0]} - {current_sub_range[1]}\n")
        current_sub_range_index = sub_ranges_list.index(current_sub_range)
    else:
        current_priv_key += 1

    return f"{current_priv_key:064x}"

def divide_subrange(sub_range, num_threads):
    start = int(sub_range[0], 16)
    end = int(sub_range[1], 16)
    step = (end - start) // num_threads

    divided_subranges = []
    for i in range(num_threads):
        subrange_start = start + i * step
        subrange_end = start + (i + 1) * step - 1 if i < num_threads - 1 else end
        divided_subranges.append((f"{subrange_start:064x}", f"{subrange_end:064x}"))

    return divided_subranges

def full_sequential(selected_range, range_index, num_threads):
    global current_priv_key

    current_priv_key += 1
    if current_priv_key > int(selected_range[1], 16):
        current_priv_key = int(selected_range[0], 16)

    return f"{current_priv_key:064x}"

def full_rand(selected_range, range_index, num_threads):
    start = int(selected_range[0], 16)
    end = int(selected_range[1], 16)

    # Проверка на случай, если диапазон слишком маленький
    if start == end:
        raise ValueError("Range is empty")

    rand_num = random.randrange(start, end + 1)
    return f"{rand_num:064x}"

def full_rand_custom(min_range, max_range, *args, **kwargs):
    return f"{random.randint(min_range, max_range):064x}"

def full_sequential_custom(min_range, max_range, *args, **kwargs):
    global current_priv_key

    current_priv_key += 1
    remaining_keys = int(max_range, 16) - current_priv_key + 1  # осталось ключей до конца диапазона
    if current_priv_key > int(max_range, 16):
        current_priv_key = int(min_range, 16)
        remaining_keys = int(max_range, 16) - current_priv_key + 1

    return f"{current_priv_key:064x}", remaining_keys

def update_progress_bar(keys_checked, total_keys, start_time, total_keys_short, total_suffix):
    if total_keys <= 0:
        return
    progress = min(keys_checked / total_keys, 1.0)
    bar_length = 40
    filled_length = int(round(bar_length * progress))

    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    keys_per_sec, speed_suffix = convert_int(keys_checked / (time.time() - start_time))
    keys_checked_short, keys_suffix = convert_int(keys_checked)

    console.print(f"[cyan]Progress: [/cyan][green]|[/green]{bar}[green]|[/green] {progress * 100:.2f}% [green]|[/green] [cyan]Speed: [/cyan][yellow]{keys_per_sec} {speed_suffix}/s[/yellow] [green]|[/green] [cyan]Checked: [/cyan][green]{keys_checked_short} {keys_suffix}/{total_keys_short} {total_suffix}[/green]", end="\r")
