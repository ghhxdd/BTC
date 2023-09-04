from functions import *
from functions import tg_id, tg_token

def search_key(key_gen_func, selected_range, search_type, target_pubkey, target_address, range_index, num_threads, custom_min_range=None, custom_max_range=None):
    start_time = time.time()
    keys_checked = 0
    priv_key = None
    remaining_keys = None
    result = None
    
    while True:
        key_gen_result = key_gen_func(selected_range, range_index, num_threads)
        if isinstance(key_gen_result, tuple) and len(key_gen_result) == 2:
            priv_key, remaining_keys = key_gen_result
        elif key_gen_result is None:
            break
        else:
            priv_key = key_gen_result

        if search_type == "1":
            int_priv_key = int(priv_key, 16)
            result = get_compressed_address(hex(int_priv_key))
        elif search_type == "2":
            int_priv_key = int(priv_key, 16)
            result = get_compressed_address(hex(int_priv_key))
        
        keys_checked += 1

        if result == target_pubkey or result == target_address:
            return priv_key, result, keys_checked, remaining_keys, time.time() - start_time

        if time.time() - start_time > 1:  # Update every 1 second
            return priv_key, result, keys_checked, remaining_keys, time.time() - start_time

    return None, None, keys_checked, time.time() - start_time, remaining_keys

def main(selected_range):
    cls()
    console.print(f'[I] [cyan]Version:[/cyan] [red]{version}[/red]')
    console.print(f'[I] [cyan]Start proogramm: [/cyan] [red]{date_str()}[/red]')
    console.print(f'[I] [cyan]Developed by[/cyan] : [green]MARKELOX[/green]\n')
    console.print(f'[I] [cyan]Your maximum number of cores[/cyan] : [green]{maxcpucount}[/green]\n')
    console.print(f'[cyan]This program is designed to search for puzzles from 1 to 160\nWorking in a multi-stream, improvements are underway today\nif you have questions or suggestions, ask in telegram:[/cyan] [green]https://t.me/markelox_off[/green]\n')
    total_keys_checked = 0
    valid_input = False
    telegram_token = None
    telegram_channel_id = None

    while not valid_input:
        telegram_enable = console.input("Do you want to send found keys to Telegram? (Y(н)/N(т)): ").lower()
        if telegram_enable not in ['y', 'n', 'т', 'н']:
            console.print("[red]Error:[/red] Please select either 'Y' or 'N'.")
        else:
            valid_input = True
    if telegram_enable in ('y', 'н'):
        telegram_token = tg_token
        telegram_channel_id = tg_id
        send_telegram(f"[I] Version:{version} Start programm: {date_str()}", telegram_channel_id, telegram_token)

    max_cpu_count = os.cpu_count()
       
    key_gen_funcs = {'1': full_rand, '2': full_sequential, '3': full_sequential_subrange}
    valid_input = False
    while not valid_input:
        key_gen_choice = console.input("\n[green]Select a search option: [/green]\n[cyan]1: Random key generator (full\custom range): [/cyan]\n[cyan]2: Sequential search of the range (full\custom range): [/cyan]\n[cyan]3: Sequential iteration of the sub-range of the range: [/cyan]")
        if key_gen_choice not in key_gen_funcs.keys():
            console.print("[red]Error:[/red] Please enter a valid option.")
        else:
            valid_input = True

    if key_gen_choice == '1':
        valid_input = False
        while not valid_input:
            rand_mode_choice = console.input("\n[green]Select random mode: [/green]\n[cyan]1: Full random range: [/cyan]\n[cyan]2: Custom random range: [/cyan]")
            if rand_mode_choice not in ['1', '2']:
                console.print("[red]Error:[/red] Please enter a valid option.")
            else:
                valid_input = True

        if rand_mode_choice == '2':
            custom_min_range = int(console.input("\n[cyan]Enter custom minimum range: [/cyan]"), 16)
            custom_max_range = int(console.input("[cyan]Enter custom maximum range: [/cyan]"), 16)
            key_gen_func = partial(full_rand_custom, custom_min_range, custom_max_range)
        else:
            key_gen_func = key_gen_funcs[key_gen_choice]

    elif key_gen_choice == '2':
        console.print('[blue]\nYou have selected the second search mode.[/blue]\n[red]THIS FEATURE DOES NOT DEPEND ON THE SELECTED CORES, IT WILL BE FIXED SOON.\nPROGRAMMATICALLY LIMITED TO 1 THREAD[/red]\n[blue]This mode iterates through the range sequentially.[/blue]')
        
        valid_input = False
        while not valid_input:
            seq_mode_choice = console.input("\n[green]Select sequential mode: [/green]\n[cyan]1: Standard range: [/cyan]\n[cyan]2: Custom range: [/cyan]")
            if seq_mode_choice not in ['1', '2']:
                console.print("[red]Error:[/red] Please enter a valid option.")
            else:
                valid_input = True

        if seq_mode_choice == '2':
            custom_min_range = console.input("\n[cyan]Enter custom minimum range: [/cyan]")
            custom_max_range = console.input("[cyan]Enter custom maximum range: [/cyan]")
            key_gen_func = partial(full_sequential_custom, custom_min_range, custom_max_range)
        else:
            key_gen_func = key_gen_funcs[key_gen_choice]

    elif key_gen_choice == '3':
        console.print('[blue]\nYou have selected the third search mode.[/blue]\n[red]ATTENTION: THIS FUNCTION IS STILL IN DEVELOPMENT AND MAY HAVE BUGS.[/red]\n[blue]This mode iterates through a range of private keys sequentially and searches for the corresponding public key and address.[/blue]')
        key_gen_func = key_gen_funcs[key_gen_choice]

    if key_gen_choice == '2':
        num_processes = 1
    else:
        valid_input = False
        while not valid_input:
            num_processes = console.input(f"\n[cyan]Enter the number of CPUs to use (max {max_cpu_count}):[/cyan] ")
            if not num_processes.isdigit():
                console.print("[red]Error:[/red] Please enter a valid integer.")
            else:
                num_processes = int(num_processes)
                if num_processes > max_cpu_count:
                    console.print(f"[red]Error:[/red] Please enter a number between 1 and {max_cpu_count}.")
                else:
                    valid_input = True

    executor = ProcessPoolExecutor(max_workers=num_processes, mp_context=multiprocessing.get_context('spawn'))


    valid_input = False
    while not valid_input:
        search_choice = console.input("\n[green]Choose a work option:[/green]\n[cyan]1: for searching by public key[/cyan]\n[cyan]2: for searching by address: [/cyan]")
        if search_choice not in ['1', '2']:
            console.print("[red]Error:[/red] Please enter a valid search option.")
        else:
            valid_input = True

    if search_choice == "1":
        console.print("\n[cyan]You have chosen to search by public key.[/cyan]")
    elif search_choice == "2":
        console.print("\n[cyan]You have chosen to search by address.[/cyan]")

    for i in range(1, len(ranges) + 1):
        r = ranges[i]
        if search_choice == "1" and r[3] is None:
            continue
    valid_input = False
    while not valid_input:
        range_index = int(console.input("\n[cyan]Choose which puzzle you want to search for (1-160): [/cyan]"))
        if range_index < 1 or range_index > len(ranges):
            console.print("[red]Error:[/red] Please enter a valid range index between 1 and 160.")
        else:
            selected_range = ranges[range_index]
            TARGET_PUBKEY = selected_range[3]
            TARGET_ADDRESS = selected_range[2]
        if search_choice == "1" and TARGET_PUBKEY is None:
            console.print("Cannot search by public key in this range. Please select another range.")
        else:
            break

    start_time = time.time()

    futures = [executor.submit(search_key, key_gen_func, selected_range, search_choice, TARGET_PUBKEY, TARGET_ADDRESS, range_index, num_processes) for _ in range(executor._max_workers)]

    if key_gen_choice == '2' and seq_mode_choice == '2':
        while not valid_input:
            output_choice = console.input("\n[green]Select the output option:[/green]\n[cyan]1: for very short output[/cyan]\n[cyan]2: for short output[/cyan]\n[cyan]3: for full output: [/cyan]\n[cyan]4: For progress-bar: [/cyan]")
            if output_choice not in ['1', '2', '3', '4']:
                console.print("[red]Error:[/red] Please enter a valid output option.")
            else:
                valid_input = True
    else:
        while not valid_input:
            output_choice = console.input("\n[green]Select the output option:[/green]\n[cyan]1: for very short output[/cyan]\n[cyan]2: for short output[/cyan]\n[cyan]3: for full output: [/cyan]")
            if output_choice not in ['1', '2', '3']:
                console.print("[red]Error:[/red] Please enter a valid output option.")
            else:
                valid_input = True

    while True:
        completed_futures = 0
        for future in as_completed(futures):
            priv_key, result, keys_checked, time_elapsed, remaining_keys = future.result()
            if priv_key is None:
                continue
            wif = ice.btc_pvk_to_wif(priv_key, False)
            total_keys_checked += keys_checked
            priv_key_hex = priv_key[2:]  # Преобразование целочисленного значения приватного ключа в шестнадцатеричную строку и удаление префикса "0x"

            if (search_choice == '1' and result == TARGET_PUBKEY) or \
            (search_choice == '2' and result == TARGET_ADDRESS):
                with open("Found.txt", "a") as f:
                    f.write(f"\nPrivate key: {priv_key_hex}\nWif: {wif}\nAddress: {result}")
                if telegram_enable and telegram_channel_id:
                    send_telegram(f"Private key: {priv_key}\nWif: {wif}\nAddress: {result}", telegram_channel_id, telegram_token)
                print(f"\nPrivate key: {priv_key_hex}\nWif: {wif}\nAddress: {result}")
                elapsed_seconds = time.time() - start_time
                print(f"Time elapsed: {elapsed_seconds:.2f} seconds")
                return
            completed_futures += 1
            if completed_futures == len(futures):
                break

        elapsed_seconds = time.time() - start_time
        speed = total_keys_checked / elapsed_seconds
        keys_per_sec, suffix = convert_int(speed)
        checked_keys, suffix1 = convert_int(total_keys_checked)
        if output_choice == '1':
            console.print(f"[cyan]Speed:[/cyan] [green]{keys_per_sec} {suffix} /s[/green] | [cyan]Keys checked: [/cyan][green]{checked_keys} {suffix1} [/green]| [cyan]Time elapsed: [/cyan][green]{elapsed_seconds:.2f}[/green] [green]seconds[/green] | [cyan]Remaining keys: [/cyan][green]{remaining_keys}[/green]", end="\r")
        elif output_choice == '2':
            if priv_key is not None and result is not None:
                console.print(f"[cyan]Speed:[/cyan] [green]{keys_per_sec} {suffix} /s[/green] | [cyan]Private: [/cyan][green]{priv_key_hex[:8]}...{priv_key_hex[-8:]}[/green] [cyan]Result: [/cyan][green]{result[:8]}...{result[-8:]}[/green] | [cyan]Time elapsed:[/cyan] [green]{elapsed_seconds:.2f}[/green] [cyan]seconds[/cyan]", end="\r")
        elif output_choice == '3':
            if priv_key is not None and result is not None:
                console.print(f"[cyan]Speed:[/cyan] [green]{keys_per_sec} {suffix} /s[/green] | [cyan]Private: [/cyan][green]{priv_key_hex}[/green] Result: {result} | [cyan]Keys checked: [/cyan][green]{checked_keys} {suffix1}[/green] | [cyan]Time elapsed: [/cyan][green]{elapsed_seconds:.2f}[/green] [cyan]seconds[/cyan]", end="\r")
        elif output_choice == '4' and key_gen_choice == '2' and seq_mode_choice == '2':
            total_keys = gmpy2.mpz(int(custom_max_range, 16)) - gmpy2.mpz(int(custom_min_range, 16)) + gmpy2.mpz(1)
            total_keys_short, total_suffix = convert_int(total_keys)
            if total_keys_checked > total_keys:
                total_keys_checked = total_keys
            update_progress_bar(np.uint64(total_keys_checked), total_keys, start_time, total_keys_short, total_suffix)


        futures = [executor.submit(search_key, key_gen_func, selected_range, search_choice, TARGET_PUBKEY, TARGET_ADDRESS, range_index, num_processes) for _ in range(executor._max_workers)]

if __name__ == "__main__":
    main(selected_range)