# app_name: PLC目標生産数変更
"""
KV-5000の目標日産数(DM1990)を確認/変更する
"""

from pathlib import Path
import configparser
from common_lib_mw import kv_com as kvc

# --- CONSTANTS -------------------------------------------
SETTING_PATH = Path("setting.ini")
DAILY_PROD_GOAL_DEVICE = 'DM1990'


# --- FUNCTIONS -------------------------------------------
def make_machine_name(input_text: str) -> str:
    """
    ユーザ入力を MC番号形式に変換する(例:"21"→"MC021")
    """
    text = input_text.strip().upper()

    if text.startswith("MC"):
        number_text = text[2:]
    else:
        number_text = text

    if not number_text.isdigit():
        raise ValueError("機械番号は数字で入力してください")
    
    return f"MC{int(number_text):03d}"


def get_ip_address(machine_name: str, setting_path: Path) -> str:
    """
    setting.ini から指定機械のIPアドレスを取得する
    """
    config = configparser.ConfigParser()
    config.read(setting_path, encoding='utf-8')

    if machine_name not in config:
        raise KeyError(f"{machine_name} は setting.ini に存在しません")

    if "IpAddress" not in config[machine_name]:
        raise KeyError(f"{machine_name} に IpAddress が設定されていません")
    
    return config[machine_name]["IpAddress"]


def get_daily_production_goal(machine_name: str) -> int:
    """
    KV-5000のDM1990の値を取得し、目標日産数として返す
    """
    ip_address = get_ip_address(machine_name, SETTING_PATH)
    
    res = kvc.read_device_u(ip_address, DAILY_PROD_GOAL_DEVICE)
    return int(res)


def set_daily_production_goal(machine_name: str, goal_value: str) -> None:
    """
    KV-5000のDM1990を変更することで、目標日産数を変更する
    """
    ip_address = get_ip_address(machine_name, SETTING_PATH)

    if not goal_value.isdigit():
        raise ValueError("設定数は数字で入力してください")

    goal_value_int = int(goal_value)
    if not 0 <= goal_value_int <= 65535:
        raise ValueError("設定値は 0～65535 の範囲で入力して下さい")

    res = kvc.write_device_u(
        ip_address,
        DAILY_PROD_GOAL_DEVICE,
        goal_value_int
        )

    if res!='OK':
        raise ConnectionError(f"PLCとの通信でエラーが発生しました(エラーコード={res})")
    


def main():
    user_input = input("接続対象の機械番号を入力してください: ")
    
    ##############################
    # 現在の目標日産数確認
    ##############################
    try:
        machine_name = make_machine_name(user_input)

        daily_prod_goal = get_daily_production_goal(machine_name)
        print(f"接続対象: {machine_name}")
        print(f"現在の目標日産数は {daily_prod_goal}です")
    
    except Exception as e:
        print("エラーが発生しました")
        print(e)
        return

    ##############################
    # 目標日産数の変更
    ##############################
    try:
        while True:
            user_input = input("日産目標数を変更しますか?(y/n): ")
            if user_input.lower()=='y':
                goal_value = input("新しい目標日産数を入力してください: ")
                set_daily_production_goal(machine_name, goal_value)
                new_goal = get_daily_production_goal(machine_name)

                print("--- 目標日産数を変更しました ---")
                print(f"変更後の目標日産数は {new_goal} です")
                break
            elif user_input.lower()=='n':
                break
            else:
                print("入力値が不正です。再入力してください")
                continue

    except Exception as e:
        print("エラーが発生しました")
        print(e)
        return

    print('---- プログラム終了 ----')
    input("何かキーを押してください")   # 自動でコンソールが閉じるのを防ぐ


if __name__=="__main__":
    main()