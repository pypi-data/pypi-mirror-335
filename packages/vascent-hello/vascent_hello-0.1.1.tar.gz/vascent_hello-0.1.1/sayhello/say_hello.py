# say_hello.py
import argparse

def main():
    parser = argparse.ArgumentParser(description='Say hello to a user')
    parser.add_argument('name', nargs='?', default='World', help='Name of the user to greet')
    args = parser.parse_args()
    print(f"Hello {args.name}!")

if __name__ == "__main__":
    main()