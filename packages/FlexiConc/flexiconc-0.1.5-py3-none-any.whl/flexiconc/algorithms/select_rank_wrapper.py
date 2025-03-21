import operator

def select_by_rank(conc, **args):
    """
    Selects lines based on rank values obtained from a selected 'algo_*' key in the ordering_result["rank_keys"]
    of the active_node, using a comparison operator and value.

    Args are dynamically validated and extracted from the schema.

    Parameters:
        conc (Union[Concordance, ConcordanceSubset]): The concordance or subset of data.
        args (dict): Arguments include:
            - active_node (object): The active node containing the ordering_result with rank_keys.
            - algo_key (str): The specific algorithm key from ordering_result["rank_keys"] to use.
                              Allowed values are those that start with "algo_". By default, the smallest key (lowest number) is used.
            - comparison_operator (str): The comparison operator ('==', '<=', '>=' ,'<', '>'). Default is "==".
            - value (number): The value to compare the rank keys against. Default is 0.

    Returns:
        dict: A dictionary containing:
            - "selected_lines": A sorted list of selected line IDs.
            - "line_count": The total number of selected lines.
    """
    # Metadata for the algorithm
    select_by_rank._algorithm_metadata = {
        "name": "Select by Rank",
        "description": (
            "Selects lines based on rank values obtained from a selected 'algo_*' key in the ordering_result['rank_keys'] "
            "of the active_node, using a comparison operator and value."
        ),
        "algorithm_type": "selection",
        "status": "experimental",
        "args_schema": {
            "type": "object",
            "properties": {
                "algo_key": {
                    "type": "string",
                    "description": (
                        "The specific algorithm key from rank_keys available at the current node."
                        "Allowed values have the form 'algo_N', and the recommended value is most often 'algo_0', i.e. the top-level ranking."
                    ),
                    "x-eval": (
                        "dict(enum=sorted([key for key in active_node.ordering_result['rank_keys'].keys() if key.startswith('algo_')], "
                        "key=lambda k: int(k.split('_')[1])), default=sorted([key for key in active_node.ordering_result['rank_keys'].keys() if key.startswith('algo_')], "
                        "key=lambda k: int(k.split('_')[1]))[0])"
                    )
                },
                "comparison_operator": {
                    "type": "string",
                    "enum": ["==", "<=", ">=", "<", ">"],
                    "description": "The comparison operator to use for rank values.",
                    "default": "=="
                },
                "value": {
                    "type": "number",
                    "description": "The value to compare the rank keys against.",
                    "default": 0
                }
            },
            "required": []
        }
    }

    # Extract arguments
    active_node = conc.active_node
    algo_key = args.get("algo_key", None)
    comparison_operator = args.get("comparison_operator", "==")
    value = args.get("value", 0)

    # Validate that active_node has ordering_result with rank_keys.
    if not hasattr(active_node, "ordering_result") or "rank_keys" not in active_node.ordering_result:
        raise ValueError("The active_node does not contain 'ordering_result' with 'rank_keys'.")

    rank_keys = active_node.ordering_result["rank_keys"]

    # If algo_key is not provided, default to the smallest key based on numeric order.
    if algo_key is None:
        algo_candidates = [key for key in rank_keys.keys() if key.startswith("algo_")]
        if not algo_candidates:
            raise ValueError("No 'algo_*' keys found in the active_node ordering_result.")
        algo_key = sorted(algo_candidates, key=lambda k: int(k.split("_")[1]))[0]

    ranks = rank_keys[algo_key]

    # Define comparison operators.
    ops = {
        "==": operator.eq,
        "<=": operator.le,
        ">=": operator.ge,
        "<": operator.lt,
        ">": operator.gt
    }
    comp_func = ops[comparison_operator]

    selected_lines = [line_id for line_id, rank in ranks.items() if comp_func(rank, value)]

    return {
        "selected_lines": sorted(selected_lines)
    }
