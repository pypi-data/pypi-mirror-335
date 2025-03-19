import enum
import random
import time


def int_to_byte32(val: int) -> bytes:
    hex_value = "{:064x}".format(val)
    return bytes.fromhex(hex_value)

def get_sub_account(account: str, sub_account_id: int) -> str:
  check_sub_account_id_param(sub_account_id)
  return account + str(sub_account_id).zfill(24)


def check_sub_account_id_param(sub_account_id: int):
  if sub_account_id not in range(0, 256):
    raise Exception("Invalid sub account id")


def generate_nonce() -> int:
  expired_at = (int(time.time()) + 60 * 1) * (1 << 20)
  random_number = random.randint(0, (1 << 20) - 1)
  return (expired_at + random_number) * 1000

def convert_enum_to_string(enum_value: enum.Enum | str) -> str:
  if isinstance(enum_value, enum.Enum):
    return enum_value.value
  return enum_value
