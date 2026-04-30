"""Smoke-test the Durunubi API and print the first 3 courses.

Run from project root:
    uv run python scripts/01_test_durunubi.py
"""

from hiking.apis.durunubi import extract_items, fetch_course_list


def main() -> None:
    response = fetch_course_list(page_no=1, num_of_rows=5)
    items = extract_items(response)

    print(f"Total fetched: {len(items)}")

    if not items:
        print("\n[!] Empty response. Check:")
        print("    - .env has DATA_GO_KR_KEY set")
        print("    - The Decoding key (not Encoding) is used")
        print("    - 두루누비 API 활용신청이 승인됨 (보통 1-24시간 소요)")
        return

    for i, item in enumerate(items[:3], start=1):
        print(f"\n--- Course {i} ---")
        for key in ("crsKorNm", "crsLocation", "crsTotlRqrmHour", "crsLevel", "crsDstnc"):
            if key in item:
                print(f"  {key}: {item[key]}")


if __name__ == "__main__":
    main()
