from vajra.hardware.scanner import scan_hardware
from vajra.catalog.loader import load_distros
from vajra.recommender.engine import recommend_distros

def main():
    hardware = scan_hardware()
    distros = load_distros()
    recommendations = recommend_distros(hardware, distros)

    print("\n=== VAJRA BI-BOOTIN: HARDWARE PROFILE ===")
    for key, value in hardware.items():
        print(f"{key:16}: {value}")

    print("\n=== RECOMMENDED LINUX DISTRIBUTIONS ===")
    for index, item in enumerate(recommendations[:5], 1):
        print(f"\n{index}. {item['name']} — {item['score']}/100")
        for reason in item["reasons"]:
            print(f"   • {reason}")
        print(f"   Download: {item['official_download_page']}")

if __name__ == "__main__":
    main()
