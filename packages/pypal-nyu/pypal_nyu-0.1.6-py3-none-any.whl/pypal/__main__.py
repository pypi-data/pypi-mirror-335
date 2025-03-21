from pypal.generator import generate_name, generate_address, generate_phone_number, generate_profile

def main():
    print("=== Example: Human Names ===")
    print(generate_name(type="human", length=3))

    print("\n=== Example: Fantasy Names ===")
    print(generate_name(type="fantasy", length=3))

    print("\n=== Example: US Short Address ===")
    print(generate_address(country="US", format="short"))

    print("\n=== Example: UK Long Address ===")
    print(generate_address(country="UK", format="long"))

    print("\n=== Example: Domestic Phone Number ===")
    print(generate_phone_number(style="domestic"))

    print("\n=== Example: International Phone Number ===")
    print(generate_phone_number(style="international"))

    print("\n=== Example: Full Profile ===")
    print(generate_profile(include_email=True, include_phone=True))

    print("\n=== Example: Profile Without Email ===")
    print(generate_profile(include_email=False, include_phone=True))

if __name__ == "__main__":
    main()
