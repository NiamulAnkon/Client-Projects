import sys

def get_int_input(prompt, default=1):
    """Helper to ensure we get a valid number from the user."""
    user_input = input(prompt).strip()
    if not user_input:
        return default
    try:
        return int(user_input)
    except ValueError:
        print(f"⚠️ Invalid number. Using default: {default}")
        return default

def collect_all_data():
    print("\n" + "="*30)
    print(" 🔐 LOGIN CREDENTIALS")
    print("="*30)
    login_phone = input("Enter Login Mobile: ").strip()
    # We collect password here so it's ready, even if you type it manually later
    # login_pass = input("Enter Login Password: ").strip()

    apps = []
    print("\n" + "="*30)
    total_apps = get_int_input("How many applications to process?: ", 1)

    for i in range(1, total_apps + 1):
        print(f"\n--- 📄 APPLICATION #{i} ---")
        webfile = input(f"Enter Main Webfile ID: ").strip().upper()
        full_name = input(f"Enter Full Name: ").strip()
        email = input(f"Enter Email: ").strip()
        personal_phone = input(f"Enter Applicant Phone: ").strip()
        f_count = get_int_input("Total Persons (Main + Family, max 5): ", 1)
        
        family_list = []
        if f_count > 1:
            print(f"\n👨‍👩‍👧‍👦 Adding {f_count - 1} additional family members:")
            for f in range(1, f_count):
                print(f"  > Member {f} Details:")
                fn = input("    Name: ").strip()
                fw = input("    Webfile: ").strip().upper()
                family_list.append({"name": fn, "webfile": fw})

        apps.append({
            "webfile": webfile,
            "name": full_name,
            "email": email,
            "phone": personal_phone,
            "family_count": f_count,
            "family_members": family_list
        })

    print("\n✅ All data collected. Starting browser...")
    return {
        "login": {"phone": login_phone},
        "apps": apps
    }