def format_concordance_line(line_df, left_node_right=False, html=False, table=False, p=["word"], style={},
                            l=-float('Inf'), u=float('Inf')):

    """
    Formats the given concordance line as a string.

    Parameters:
    - line_df (DataFrame): The dataframe representing the line.
    - left_node_right: A boolean flag. If set to True, it will return a dictionary structure
      dividing the line into left, node, and right sections. If set to False, it will just
      format the line as a single string.

    Returns:
    - A formatted string or a dictionary structure with the 'left', 'node', and 'right'
      parts of the line, depending on the `left_node_right` parameter.
    """

    # If just formatting the entire line as a single string
    if not left_node_right:
        output = ''
        right_punctuation = ['.', '?', '!', ',', '…', ';', ':', '"', "'", "n't"]
        left_punctuation = ['(', '`', '``']
        words = list(line_df.word.astype(str))
        offsets = list(line_df.offset)

        # Check if there are spaces provided in the concordance, else default to None
        spaces = list(line_df.space.astype(str)) if 'space' in line_df else None

        for i, word in enumerate(words):
            if offsets[i] < l or offsets[i] > u:
                continue
            if 'offset' in style and offsets[i] in style['offset']:
                output += style['offset'][offsets[i]].format(word)
            else:
                output += word

            # If explicit spaces are provided, use them
            if spaces is not None:
                output += spaces[i]
            else:
                # Check conditions to decide whether to add space or not
                if word in left_punctuation:
                    continue
                elif i < len(words) - 1 and (words[i + 1] in right_punctuation or words[i + 1][0] == "'"):
                    continue
                else:
                    output += ' '

        return output

    # If splitting the line into left, node, and right sections
    else:
        return {
            'left': format_concordance_line(line_df[line_df["offset"] < 0], html=html, table=table, p=p, style=style),
            'node': format_concordance_line(line_df[line_df["offset"] == 0], html=html, table=table, p=p, style=style),
            'right': format_concordance_line(line_df[line_df["offset"] > 0], html=html, table=table, p=p, style=style)
        }


def generate_concordance_html(concordance, node, n=25, n_groups=None, token_attr='word', metadata_columns=None):
    """
    Generates HTML for concordance lines from the tokens in the subset at the given node,
    with optional custom metadata columns inserted between the line ID and the KWIC display.

    Parameters:
        concordance: The Concordance object.
        node: The analysis tree node whose subset is to be displayed.
        n (int, optional): The number of lines to display per partition or overall. Default is 25.
        n_groups (int, optional): If concordance view is partitioned, show only first `n_groups` groups. Default None shows all groups.
        token_attr (str, optional): The token attribute to display (e.g., 'word', 'lemma'). Default is 'word'.
        metadata_columns (list of str, optional): A list of metadata column names to display for each line.
            These columns will be shown between the "Line ID" column and the KWIC display columns.

    Returns:
        str: An HTML string representing the concordance lines.
    """
    # Get the subset at the specified node.
    subset = concordance.subset_at_node(node)
    tokens = subset.tokens
    metadata = subset.metadata

    # Start building the HTML.
    html_output = """
    <style>
        table.concordance {
            border-collapse: collapse;
            width: 100%;
            table-layout: auto;
        }
        table.concordance th, table.concordance td {
            border: 1px solid #dddddd;
            padding: 4px;
            vertical-align: top;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        table.concordance th {
            background-color: #f2f2f2;
            text-align: center;
        }
        table.concordance th.line-id, table.concordance td.line-id {
            text-align: center;
            white-space: nowrap;
        }
        table.concordance th.metadata, table.concordance td.metadata {
            text-align: center;
            white-space: nowrap;
        }
        table.concordance th.left-context, table.concordance td.left-context {
            text-align: right;
            overflow: hidden;
            white-space: nowrap;
            width: 40%;
            max-width: 0px;
        }
        table.concordance th.node, table.concordance td.node {
            text-align: center;
            font-weight: bold;
            white-space: nowrap;
        }
        table.concordance th.right-context, table.concordance td.right-context {
            text-align: left;
            overflow: hidden;
            white-space: nowrap;
            width: 40%;
            max-width: 0px;
        }
        table.concordance div.left-context {
            float: right;
            white-space: nowrap;
        }
        table.concordance div.right-context {
            float: left;
            white-space: nowrap;
        }
    </style>
    <table class="concordance">
        <colgroup>
            <col>
    """
    # If metadata_columns are provided, add one <col> per column.
    if metadata_columns:
        for _ in metadata_columns:
            html_output += "            <col>\n"
    html_output += """            <col>
            <col>
            <col>
        </colgroup>
        <tr>
            <th class="line-id">Line ID</th>
    """
    # Add header cells for custom metadata columns.
    if metadata_columns:
        for col in metadata_columns:
            html_output += f'            <th class="metadata">{col}</th>\n'
    html_output += """            <th class="left-context">Left Context</th>
            <th class="node">Node</th>
            <th class="right-context">Right Context</th>
        </tr>
    """

    # Helper function: generate HTML rows for given line IDs.
    def _generate_lines_html(subset, line_ids, token_attr, metadata_columns=None):
        tokens = subset.tokens
        metadata = subset.metadata
        html_rows = ""
        for line_id in line_ids:
            # Get tokens for this line and sort by offset and id_in_line.
            line_tokens = tokens[tokens['line_id'] == line_id].sort_values(by=['offset', 'id_in_line'])
            # Separate tokens into left, node, and right based on offset.
            left_tokens = line_tokens[line_tokens['offset'] < 0]
            node_tokens = line_tokens[line_tokens['offset'] == 0]
            right_tokens = line_tokens[line_tokens['offset'] > 0]

            def tokens_to_text(tokens_df):
                text = ''
                previous_token = ''
                for token in tokens_df[token_attr]:
                    token = str(token)
                    if token in ['.', ',', '!', '?', ';', ':', "'", '"', ')', ']', '}', '...']:
                        text += token
                    elif previous_token in ['(', '[', '{', '“']:
                        text += token
                    else:
                        if text and not text.endswith(' '):
                            text += ' '
                        text += token
                    previous_token = token
                return text.strip()

            left_text = tokens_to_text(left_tokens)
            node_text = tokens_to_text(node_tokens)
            right_text = tokens_to_text(right_tokens)

            # Escape HTML special characters.
            import html
            left_text = html.escape(left_text)
            node_text = html.escape(node_text)
            right_text = html.escape(right_text)

            # Get metadata values for custom columns.
            metadata_cells = ""
            if metadata_columns:
                # Find the metadata row for this line_id. (Assuming line_id is unique.)
                row = metadata.loc[metadata['line_id'] == line_id]
                if not row.empty:
                    row = row.iloc[0]
                    for col in metadata_columns:
                        metadata_cells += f'<td class="metadata">{html.escape(str(row.get(col, "")))}</td>\n'
                else:
                    for _ in metadata_columns:
                        metadata_cells += f'<td class="metadata"></td>\n'

            # Add the row HTML.
            html_rows += f"""
            <tr>
                <td class="line-id">{line_id}</td>
                {metadata_cells}
                <td class="left-context"><div class="left-context">{left_text}</div></td>
                <td class="node">{node_text}</td>
                <td class="right-context"><div class="right-context">{right_text}</div></td>
            </tr>
            """
        return html_rows

    # Process partitions if available.
    if hasattr(node, 'grouping_result') and 'partitions' in node.grouping_result:
        partitions = node.grouping_result['partitions']
        for i, partition in enumerate(partitions):
            if n_groups is not None and i >= n_groups:
                break
            partition_id = partition.get('id', 0)
            partition_label = partition.get('label', f'Partition {partition_id}')
            line_ids = partition.get('line_ids', [])
            line_count = len(line_ids)

            # Apply ordering if available.
            if hasattr(node, 'ordering_result') and 'sort_keys' in node.ordering_result:
                partition_sort_keys = {line_id: node.ordering_result["sort_keys"][line_id]
                                       for line_id in line_ids if line_id in node.ordering_result["sort_keys"]}
                sorted_line_ids = sorted(partition_sort_keys, key=partition_sort_keys.get)
            else:
                sorted_line_ids = line_ids

            partition_line_ids = sorted_line_ids[:n]

            # Add a partition header row.
            html_output += f"""
            <tr>
                <td style="text-align: center;" colspan="{4 + (len(metadata_columns) if metadata_columns else 0)}">
                    <b>{partition_label} ({line_count} line{'s' if line_count != 1 else ''})</b>
                </td>
            </tr>
            """

            # Generate HTML for lines in this partition.
            html_output += _generate_lines_html(subset, partition_line_ids, token_attr, metadata_columns)
    else:
        # Non-partitioned node.
        line_ids = metadata['line_id'].unique().tolist()
        if hasattr(node, 'ordering_result') and 'sort_keys' in node.ordering_result:
            sort_keys = node.ordering_result['sort_keys']
            node_sort_keys = {line_id: sort_keys[line_id] for line_id in line_ids if line_id in sort_keys}
            sorted_line_ids = sorted(node_sort_keys, key=node_sort_keys.get)
        else:
            sorted_line_ids = line_ids

        selected_line_ids = sorted_line_ids[:n]
        html_output += _generate_lines_html(subset, selected_line_ids, token_attr, metadata_columns)

    html_output += "</table>"
    return html_output


def _generate_lines_html(subset, line_ids, token_attr):
    """
    Helper function to generate HTML rows for given line IDs.

    Parameters:
    - subset: The ConcordanceSubset object.
    - line_ids (list): List of line IDs to include.
    - token_attr (str): The token attribute to display.

    Returns:
    - str: An HTML string representing the concordance lines.
    """
    tokens = subset.tokens
    metadata = subset.metadata

    html_rows = ""

    for line_id in line_ids:
        # Get tokens for this line
        line_tokens = tokens[tokens['line_id'] == line_id]

        # Sort tokens by offset and id_in_line to preserve order
        line_tokens = line_tokens.sort_values(by=['offset', 'id_in_line'])

        # Separate tokens into left, node, and right based on offset
        left_tokens = line_tokens[line_tokens['offset'] < 0]
        node_tokens = line_tokens[line_tokens['offset'] == 0]
        right_tokens = line_tokens[line_tokens['offset'] > 0]

        # Reconstruct text from tokens
        def tokens_to_text(tokens):
            text = ''
            previous_token = ''
            for token in tokens[token_attr]:
                token = str(token)
                if token in ['.', ',', '!', '?', ';', ':', "'", '"', ')', ']', '}', '...']:
                    text += token
                elif previous_token in ['(', '[', '{', '“']:
                    text += token
                else:
                    if text and not text.endswith(' '):
                        text += ' '  # Non-breaking space
                    text += token
                previous_token = token
            return text.strip()

        left_text = tokens_to_text(left_tokens)
        node_text = tokens_to_text(node_tokens)
        right_text = tokens_to_text(right_tokens)

        # Escape HTML special characters
        import html
        left_text = html.escape(left_text)
        node_text = html.escape(node_text)
        right_text = html.escape(right_text)

        # Add the reconstructed texts to the HTML
        html_rows += f"""
        <tr>
            <td class="line-id">{line_id}</td>
            <td class="left-context"><div class="left-context">{left_text}</div></td>
            <td class="node">{node_text}</td>
            <td class="right-context"><div class="right-context">{right_text}</div></td>
        </tr>
        """

    return html_rows


def generate_analysis_tree_html(concordance, suppress_line_info=True, mark=None):
    """
    Generates an HTML representation of the analysis tree in a human-readable manner.

    Parameters:
        concordance: The Concordance object.
        suppress_line_info (bool, optional): If True, suppresses output of 'selected_lines',
            'order_result', 'sort_keys', and 'rank_keys'. Default is True.

    Returns:
        str: An HTML string representing the analysis tree.
    """
    # Display the query above the tree.
    html_output = (
        f"<div style='margin-bottom:10px;'><strong>Query:</strong> "
        f"{concordance.info.get('query', '')}</div>\n<ul style='list-style-type:none;'>\n"
    )

    def process_node(node):
        nt = node.node_type
        node_id = node.id
        depth = node.depth
        has_children = bool(node.children)
        # Use 👉 for marked node, 🔎 for subset nodes and 🔀 for arrangement nodes.
        icon = "🔎" if nt == "subset" else "🔀"
        if mark is not None and node_id == mark:
            icon = "👉 " + icon

        indent = "    " * depth

        # For subset nodes, display the line count.
        line_count = f'({node.line_count})' if nt == "subset" else ""
        html = f"{indent}<li>[{node_id}] {icon} {nt} {line_count}: "

        # Add algorithm information if available.
        if hasattr(node, "algorithms"):
            algo_html = ""
            i = 0
            for algo_type in node.algorithms:
                algos = node.algorithms[algo_type]
                if algos is None:
                    continue
                if not isinstance(algos, list):
                    algos = [algos]
                for a in algos:
                    if i > 0:
                        algo_html += "<br/>"
                    i += 1
                    args = a['args'].copy()
                    if suppress_line_info:
                        args.pop('active_node', None)
                        args.pop('selected_lines', None)
                        args.pop('order_result', None)
                        args.pop('sort_keys', None)
                        args.pop('rank_keys', None)
                    algo_html += f"&#9881; {a['algorithm_name']} {args}"
            html += algo_html
        html += "</li>\n"

        # Process child nodes recursively.
        if has_children:
            html += f"{indent}<ul style='list-style-type:none;'>\n"
            for child in node.children:
                html += process_node(child)
            html += f"{indent}</ul>\n"

        return html

    html_output += process_node(concordance.root)
    html_output += "</ul>\n"

    return html_output
