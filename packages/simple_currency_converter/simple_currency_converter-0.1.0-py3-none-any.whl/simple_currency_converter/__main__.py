import argparse
from .currency_codes import all_codes, common_codes, crypto_codes
from .core import convert

def list_currencies(to_print: dict):
    for code, name in to_print.items():
        print(f"{code} - {name}")

def main():
    parser = argparse.ArgumentParser(description="Currency conversion tool")
    parser.add_argument("currency_from", type=str, help="Currency code to convert from", nargs='?')
    parser.add_argument("currency_to", type=str, help="Currency code to convert to", nargs='?')
    parser.add_argument("amount", type=float, help="Amount to convert", default=1, nargs='?')
    # List the currency codes
    parser.add_argument("--list-all-currencies", "--list-all", action="store_true", help="List all currency codes", default=False)
    parser.add_argument("--list-common-currencies", "--list-common", action="store_true", help="List all common currency codes", default=False)
    parser.add_argument("--list-crypto-currencies", "--list-crypto", action="store_true", help="List all crypto currency codes", default=False)
    args = parser.parse_args()
    if args.list_all_currencies:
        list_currencies(all_codes)
    elif args.list_common_currencies:
        list_currencies(common_codes)
    elif args.list_crypto_currencies:
        list_currencies(crypto_codes)
    else:
        try:
            assert args.currency_from and args.currency_to and args.amount, "Missing required arguments"
            assert args.currency_from.lower() in all_codes, f"Invalid currency code: {args.currency_from}"
            assert args.currency_to.lower() in all_codes, f"Invalid currency code: {args.currency_to}"
            print(f"{convert(args.currency_from.lower(), args.currency_to.lower(), args.amount):.8f}")
        except AssertionError as e:
            print(e)
            parser.print_help()

if __name__ == "__main__":
    main() 