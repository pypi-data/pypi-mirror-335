import re
import operator
from flexiconc.utils.line_operations import extract_words_at_offset

def select_by_token_attribute(conc, **args):
    """
    Selects lines based on a positional attribute at a given offset.

    Args are dynamically validated and extracted from the schema.

    Parameters:
      - conc (Union[Concordance, ConcordanceSubset]): The full concordance or a subset of it.
      - **kwargs: Arguments defined dynamically in the schema.

    Returns:
      - dict: A dictionary containing:
          - "selected_lines": A list of line IDs where the condition is met.
    """
    # Metadata for the algorithm
    select_by_token_attribute._algorithm_metadata = {
        "name": "Select by a Token-Level Attribute",
        "description": "Selects lines based on the specified token-level attribute at a given offset, with optional case-sensitivity, regex matching, or numeric comparison.",
        "algorithm_type": "selection",
        "args_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": ["string", "number"],
                    "description": "The value to match against.",
                    "default": ""
                },
                "tokens_attribute": {
                    "type": "string",
                    "description": "The positional attribute to check (e.g., 'word').",
                    "default": "word",
                    "x-eval": "dict(enum=list(set(conc.tokens.columns) - {'id_in_line', 'line_id', 'offset'}))"
                },
                "offset": {
                    "type": "integer",
                    "description": "The offset from the concordance node to apply the check.",
                    "default": 0,
                    "x-eval": "dict(minimum=min(conc.tokens['offset']), maximum=max(conc.tokens['offset']))"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "If True, performs a case-sensitive match (for string values).",
                    "default": False
                },
                "regex": {
                    "type": "boolean",
                    "description": "If True, uses regex matching instead of exact matching (for string values).",
                    "default": False
                },
                "comparison_operator": {
                    "type": "string",
                    "enum": ["==", "<", ">", "<=", ">="],
                    "description": "Comparison operator for numeric values. Ignored for string values.",
                    "default": "=="
                },
                "negative": {
                    "type": "boolean",
                    "description": "If True, inverts the selection (i.e., selects lines where the match fails).",
                    "default": False
                }
            },
            "required": ["value"]
        }
    }

    # Extract arguments
    tokens_attribute = args.get("tokens_attribute", "word")
    offset = args.get("offset", 0)
    value = args.get("value", "")
    case_sensitive = args.get("case_sensitive", False)
    regex = args.get("regex", False)
    negative = args.get("negative", False)
    comparison_operator = args.get("comparison_operator", "==")

    # Extract words or tokens based on the positional attribute and offset
    items = list(extract_words_at_offset(conc.tokens, p=tokens_attribute, offset=offset))
    # Retrieve the line IDs for this concordance
    line_ids = conc.metadata.index.tolist()

    # Determine whether to perform numeric or string matching
    if isinstance(value, (int, float)):
        # Define allowed operators for numeric comparison
        ops = {
            "==": operator.eq,
            "<": operator.lt,
            ">": operator.gt,
            "<=": operator.le,
            ">=": operator.ge
        }
        comp_func = ops.get(comparison_operator)
        if comp_func is None:
            raise ValueError(f"Invalid comparison_operator '{comparison_operator}' for numeric comparison.")
        # Attempt to convert token values to float for comparison
        selection = []
        for item in items:
            try:
                token_num = float(item)
                match = comp_func(token_num, value)
            except (ValueError, TypeError):
                match = False
            selection.append(1 if match else 0)
    else:
        # Treat value as a string
        if regex:
            # Set regex flags based on case sensitivity
            flags = 0 if case_sensitive else re.IGNORECASE
            selection = [1 if re.search(value, item, flags=flags) else 0 for item in items]
        else:
            if not case_sensitive:
                value_lower = value.lower()
                selection = [1 if item.lower() == value_lower else 0 for item in items]
            else:
                selection = [1 if item == value else 0 for item in items]

    # Invert selection if negative flag is enabled
    if negative:
        selection = [1 - x for x in selection]

    # Map selection to corresponding line IDs
    selected_lines = [line_ids[i] for i, flag in enumerate(selection) if flag == 1]

    return {"selected_lines": selected_lines}