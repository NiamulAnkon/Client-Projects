def collect_application_inputs():
    applications = []

    while True:
        try:
            total = int(input("How many applications do you want to process? : "))
            if total <= 0:
                raise ValueError
            break
        except ValueError:
            print("❌ Please enter a valid number.")

    while True:
        try:
            family_count = int(input("Enter family count (same for all): "))
            if family_count <= 0:
                raise ValueError
            break
        except ValueError:
            print("❌ Please enter a valid family count.")

    for i in range(1, total + 1):
        while True:
            webfile = input(f"Enter webfile number {i}: ").strip()
            if webfile:
                applications.append({
                    "webfile": webfile,
                    "family_count": family_count
                })
                break
            else:
                print("❌ Webfile cannot be empty.")

    print(f"\n✔ Loaded {len(applications)} applications")
    print(f"✔ Family count set to {family_count}\n")

    return applications
