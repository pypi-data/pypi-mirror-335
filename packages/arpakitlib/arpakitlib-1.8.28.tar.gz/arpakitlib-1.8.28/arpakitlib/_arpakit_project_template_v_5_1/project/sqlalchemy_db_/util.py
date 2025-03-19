from uuid import uuid4

from arpakitlib.ar_datetime_util import now_utc_dt


def generate_default_api_key() -> str:
    return (
        f"apikey"
        f"{str(uuid4()).replace('-', '')}"
        f"{str(now_utc_dt().timestamp()).replace('.', '')}"
    )


def generate_default_long_id():
    return (
        f"longid"
        f"{str(uuid4()).replace('-', '')}"
        f"{str(now_utc_dt().timestamp()).replace('.', '')}"
    )


def __example():
    print(generate_default_api_key())
    print(generate_default_long_id())


if __name__ == '__main__':
    __example()
