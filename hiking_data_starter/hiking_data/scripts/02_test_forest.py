"""Smoke test for the Forest Service mountain info API."""

from hiking.apis import forest


def main() -> None:
    print("Fetching one page of mountain info...")
    response = forest.fetch_mountain_list(page_no=1, num_of_rows=5)
    
    items = forest.extract_items(response)
    print(f"Total fetched: {len(items)}\n")

    for i, item in enumerate(items, 1):
        name = item.get("mntiname", "N/A")
        region = item.get("mntiadd", "N/A")
        height = item.get("mntihigh", "N/A")
        details = item.get("mntidetails", "N/A")
        
        # limit details length for display
        if isinstance(details, str) and len(details) > 50:
            details = details[:47] + "..."
            
        print(f"--- Mountain {i} ---")
        print(f"  Name: {name}")
        print(f"  Region: {region}")
        print(f"  Height: {height}m")
        print(f"  Details: {details}\n")


if __name__ == "__main__":
    main()
