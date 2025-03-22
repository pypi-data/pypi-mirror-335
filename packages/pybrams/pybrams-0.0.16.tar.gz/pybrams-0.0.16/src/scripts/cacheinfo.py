from pybrams.utils import Cache

if __name__ == "__main__":

    data = Cache.stats()
    print(f"""
        Number of files : {data.get("number_of_files")}
        Total size : {data.get("total_size_bytes")} B
        Total size : {data.get("total_size_kb")} KB
        Total size : {data.get("total_size_mb")} MB
    """)
