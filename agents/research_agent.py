from concurrent.futures import ThreadPoolExecutor, as_completed

from tools.web_search import web_search


# ============================================================
# SEARCH SINGLE QUERY
# ============================================================

def search_single_query(
    query: str,
    tavily_api_key: str
) -> list:

    print(
        f"\n🔎 Searching: {query}"
    )

    try:

        results = web_search(
            query=query,
            tavily_api_key=tavily_api_key
        )

        return results

    except Exception as e:

        print(
            f"❌ Search failed: {query}"
        )

        print(
            f"Error: {e}"
        )

        return []


# ============================================================
# RESEARCH TOPIC
# ============================================================

def research_topic(
    topic: str,
    queries: list[str],
    tavily_api_key: str
) -> list:

    if not tavily_api_key:

        raise ValueError(
            "Tavily API key is missing."
        )

    if not queries:

        print(
            "\n⚠️ No research queries provided."
        )

        return []

    print(
        "\n⚡ STARTING PARALLEL RESEARCH"
    )

    all_results = []

    worker_count = min(
        6,
        len(queries)
    )

    # --------------------------------------------------------
    # PARALLEL SEARCH
    # --------------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=worker_count
    ) as executor:

        future_to_query = {}

        for query in queries:

            future = executor.submit(
                search_single_query,
                query,
                tavily_api_key
            )

            future_to_query[
                future
            ] = query

        for future in as_completed(
            future_to_query
        ):

            query = future_to_query.get(
                future,
                "Unknown query"
            )

            try:

                results = future.result()

                all_results.extend(
                    results
                )

                print(
                    f"✅ Completed: "
                    f"{query} "
                    f"({len(results)} sources)"
                )

            except Exception as e:

                print(
                    f"❌ Failed: {query}"
                )

                print(
                    f"Error: {e}"
                )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_results = []

    seen_urls = set()

    for source in all_results:

        if not source.url:
            continue

        if source.url in seen_urls:
            continue

        seen_urls.add(
            source.url
        )

        unique_results.append(
            source
        )

    # --------------------------------------------------------
    # QUALITY SORT
    # --------------------------------------------------------

    unique_results.sort(
        key=lambda source:
        source.quality_score,
        reverse=True
    )

    print(
        "\n📚 PARALLEL RESEARCH COMPLETE"
    )

    print(
        f"Total raw sources: "
        f"{len(all_results)}"
    )

    print(
        f"Unique sources: "
        f"{len(unique_results)}"
    )

    return unique_results