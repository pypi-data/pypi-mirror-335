def rank_kwic_grouper(conc, **args):
    """
    Ranks lines based on the count of a search term within a specific positional attribute column
    within a given window (KWIC). Additionally, returns token spans for matching tokens.

    Args are dynamically validated and extracted from the schema.

    Parameters:
    - conc (Union[Concordance, ConcordanceSubset]): The full concordance or a subset of it.
    - **kwargs: Arguments defined dynamically in the schema.

    Returns:
    - dict: A dictionary containing:
        - "rank_keys": A mapping from line IDs to their ranking values based on the count of the search term.
        - "token_spans": A DataFrame with columns:
              id, line_id, start_id_in_line, end_id_in_line, category, weight.
          Here, category is "A", weight is 1, and since each span is one token long,
          start_id_in_line equals end_id_in_line (an inclusive index).
    """

    # Metadata for the algorithm
    rank_kwic_grouper._algorithm_metadata = {
        "name": "KWIC Grouper Ranker",
        "description": "Ranks lines based on the count of a search term in a specified positional attribute within a window.",
        "algorithm_type": "ranking",
        "args_schema": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The term to search for within the tokens.",
                },
                "tokens_attribute": {
                    "type": "string",
                    "description": "The positional attribute to search within (e.g., 'word').",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "regex": {
                    "type": "boolean",
                    "description": "If True, use regex for matching the search term.",
                    "default": False
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "If True, the search is case-sensitive.",
                    "default": False
                },
                "include_node": {
                    "type": "boolean",
                    "description": "If True, include node-level tokens in the search.",
                    "default": False
                },
                "window_start": {
                    "type": "integer",
                    "description": "The lower bound of the window (offset range).",
                    "x-eval": "dict(minimum=min(conc.tokens['offset']))"
                },
                "window_end": {
                    "type": "integer",
                    "description": "The upper bound of the window (offset range).",
                    "x-eval": "dict(maximum=max(conc.tokens['offset']))"
                },
                "count_types": {
                    "type": "boolean",
                    "description": "If True, count unique types within each line; otherwise, count all matches.",
                    "default": True
                }
            },
            "required": ["search_term"]
        }
    }

    # Extract arguments
    search_term = args.get("search_term")
    tokens_attribute = args.get("tokens_attribute", "word")
    regex = args.get("regex", False)
    case_sensitive = args.get("case_sensitive", False)
    include_node = args.get("include_node", False)
    window_start = args.get("window_start", float('-inf'))
    window_end = args.get("window_end", float('inf'))
    count_types = args.get("count_types", True)

    # Step 1: Filter tokens globally based on the specified window (offset range)
    filtered_tokens = conc.tokens[
        (conc.tokens["offset"] >= window_start) & (conc.tokens["offset"] <= window_end)
        ]

    # Step 2: Prepare the column to check against the search term
    values_to_check = filtered_tokens[tokens_attribute].astype(str)

    # Step 3: Apply search term matching based on regex and case sensitivity options
    if regex:
        match_condition = values_to_check.str.contains(search_term, case=case_sensitive, na=False,
                                                       regex=True)
    else:
        # If case-sensitive is False, lower the search term and values for comparison
        if not case_sensitive:
            search_term = search_term.lower()
            values_to_check = values_to_check.str.lower()
        match_condition = values_to_check == search_term

    # Step 4: Apply node-level filtering if specified (exclude node tokens if include_node is False)
    if not include_node:
        match_condition &= (filtered_tokens["offset"] != 0)

    # Step 5: Filter the tokens DataFrame using the matching condition
    matching_tokens = filtered_tokens[match_condition].copy()

    # Step 6: Build token_spans DataFrame BEFORE removing duplicates.
    token_spans = matching_tokens.reset_index(drop=True)
    # For each token, define a span that is one token long:
    token_spans["start_id_in_line"] = token_spans["id_in_line"]
    token_spans["end_id_in_line"] = token_spans["id_in_line"]
    token_spans["category"] = "A"
    token_spans["weight"] = 1
    token_spans = token_spans[["line_id", "start_id_in_line", "end_id_in_line", "category", "weight"]]

    # Step 7: If count_types is True, remove duplicate types within each line, accounting for case sensitivity
    if count_types:
        if not case_sensitive:
            matching_tokens[tokens_attribute] = matching_tokens[tokens_attribute].str.lower()
        # Remove duplicates based on line_id and the token attribute
        matching_tokens = matching_tokens.drop_duplicates(subset=['line_id', tokens_attribute])

    # Step 8: Group the (now deduplicated) tokens by line_id and count the occurrences within each line
    line_counts = matching_tokens.groupby('line_id').size().reindex(conc.metadata.index, fill_value=0)
    rank_keys = line_counts.to_dict()

    return {"rank_keys": rank_keys, "token_spans": token_spans}

