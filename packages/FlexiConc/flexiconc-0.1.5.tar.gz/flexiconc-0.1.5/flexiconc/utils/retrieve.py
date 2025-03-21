import pandas as pd
from typing import Optional, List

from flexiconc.concordance import AnalysisTreeNode
from flexiconc.visualization.html_visualizer import format_concordance_line
from flexiconc import CONFIG


def retrieve_from_cwb(
        self,
        registry_dir: Optional[str] = None,
        corpus_name: str = "",
        query: str = "",
        tokens_attrs: Optional[List[str]] = None,
        metadata_attrs: Optional[List[str]] = None,
        corpus = None,
        context: int = 20,
) -> None:
    """
    Retrieves a concordance from the CWB (Corpus Workbench), processes the data, and updates the Concordance object.

    Parameters:
    - registry_dir (Optional[str], default=None): The path to the CWB registry directory. If None, it uses the default configuration.
    - corpus_name (str, default="DNOV-CWB"): The name of the corpus in CWB.
    - query (str, default=""): The query string used to retrieve concordance lines.
    - tokens_attrs (Optional[List[str]], default=None): A list of positional (token-level) attributes to display. Defaults to all positional attributes.
    - metadata_attrs (Optional[List[str]], default=None): A list of structural (metadata-level) attributes to display. Defaults to all structural attributes.
    - corpus (ccc.Corpus): An already initialized cwb_ccc Corpus object (use this at own risk)
    - context: Number of tokens of left and right context to include (defaults to 20 as in cwb-ccc)

    Updates the following attributes of the Concordance object:
    - self.query: The query string used.
    - self.data: A DataFrame containing the concordance lines.
    - self.tokens: A DataFrame containing token-level information.
    - self.active_node: Set to the root node of the analysis tree.
    - self.labels: An ordered dictionary initialized to empty.
    """

    from ccc import Corpus

    # Set the registry directory from the configuration if not provided
    if registry_dir is None:
        registry_dir = CONFIG.get('Paths', 'CWB_REGISTRY_DIR')

    # Load the corpus based on the provided directory and corpus name
    if not corpus:
        corpus = Corpus(corpus_name=corpus_name, registry_dir=registry_dir)

    # Set default metadata and token-level attributes if not provided
    if metadata_attrs is None:
        metadata_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 's-Att', 'attribute'])
    if tokens_attrs is None:
        tokens_attrs = list(
            corpus.available_attributes().loc[corpus.available_attributes()['type'] == 'p-Att', 'attribute'])

    # Execute the query on the corpus
    dump = corpus.query(query, context=context)

    # Convert the results of the query to a dataframe
    df = dump.concordance(p_show=tokens_attrs, s_show=list(metadata_attrs), cut_off=len(dump.df), form="dataframe")

    # Rename metadata columns if provided
    if isinstance(metadata_attrs, dict):
        df.rename(columns=metadata_attrs, inplace=True)

    # Format the dataframe using the `format_concordance_line` function for display
    df["displayString"] = df["dataframe"].apply(format_concordance_line)
    df["displayStringTripartite"] = df["dataframe"].apply(format_concordance_line, args=(True,))

    # Assign a unique ID to each row in the dataframe and set it as index
    # ... but FlexiConc now expects a real column `line_id` with this information
    df["line_id"] = df["id"] = range(len(df))
    df.set_index("id", inplace=True)

    # Extract tokens and associate them with their respective line IDs
    token_dfs = []
    for index, nested_df in df['dataframe'].items():
        # Ensure 'cpos' is a column and not an index
        nested_df = nested_df.reset_index() if 'cpos' in nested_df.index.names else nested_df

        # Calculate 'id_in_line' as the difference between 'cpos' and 'context'
        nested_df = nested_df.assign(line_id=index)
        nested_df['id_in_line'] = nested_df['cpos'] - df.loc[index, 'context']

        token_dfs.append(nested_df)

    tokens = pd.concat(token_dfs).reset_index(drop=True)
    tokens.index.name = 'id'

    # Rename token-level columns if provided
    if isinstance(tokens_attrs, dict):
        df.rename(columns=tokens_attrs, inplace=True)

    # Create the matches DataFrame using the index directly for aggregation
    matches = tokens[tokens['offset'] == 0].groupby('line_id').apply(
        lambda group: pd.Series({
            'match_start': group.index.min(),  # Get the minimum index value for match_start
            'match_end': group.index.max()  # Get the maximum index value for match_end
        })
    ).reset_index()

    # Add 'slot' column to the matches DataFrame and populate it with 0's
    matches['slot'] = 0

    # Remove the 'dataframe' column before assigning metadata
    df.drop(columns=['dataframe'], inplace=True)

    # Update the object's attributes with the resulting data
    self.metadata = df
    self.tokens = tokens
    self.matches = matches
    self.info["query"] = query
    self.root = AnalysisTreeNode(id=0, node_type="subset", parent=None, concordance=self, line_count=len(self.metadata), label="root", selected_lines=list(range(len(self.metadata))))
    self.node_counter = 1


def retrieve_from_clic(
    self,
    query: List[str],
    corpora: str,
    subset: str = "all",
    contextsize: int = 20,
    api_base_url: str = "https://clic-fiction.com/api/concordance",
    # api_base_url: str = "https://clic.bham.ac.uk/api/concordance",
    metadata_attrs: Optional[List[str]] = None,
    tokens_attrs: Optional[List[str]] = None,
) -> None:
    """
    Retrieves a concordance from the CLiC API, processes the data, and updates the Concordance object.

    Parameters:
      - query (List[str]): The query strings used to retrieve concordance lines.
      - corpora (str): The corpus or corpora to search within.
      - subset (str): The subset of the corpora to search ('all', 'quote', 'nonquote', 'shortsus', 'longsus').
      - contextsize (int): The number of context words on each side.
      - api_base_url (str): The base URL of the CLiC API.
      - metadata_attrs (Optional[List[str]]): List of metadata attributes to include.
      - tokens_attrs (Optional[List[str]]): List of token-level attributes to include.

    Updates:
      - self.metadata: DataFrame of structural metadata.
      - self.tokens: DataFrame of token-level information.
      - self.matches: DataFrame of match information.
      - self.info["query"]: Stores the query used.
      - self.root: Initializes the analysis tree with a root node.
    """
    import requests
    import pandas as pd
    import re
    import string

    if metadata_attrs is None:
        metadata_attrs = ['text_id', 'chapter', 'paragraph', 'sentence']
    if tokens_attrs is None:
        tokens_attrs = ['word']

    data = []
    for q in query:
        params = {
            'q': q,
            'corpora': corpora,
            'subset': subset,
            'contextsize': contextsize
        }
        response = requests.get(api_base_url, params=params)
        response.raise_for_status()
        data += response.json().get('data', [])

    if not data:
        raise ValueError(f"No data returned from CLiC API for the provided set of queries.")

    metadata_list = []
    token_entries = []
    matches_list = []
    global_token_id = 0
    token_pattern = re.compile(r'(\w+(?:-\w+)?|[^\w\s]+)')

    for line_id, line_data in enumerate(data):
        left_context = line_data[0]
        node = line_data[1]
        right_context = line_data[2]
        corpus_info = line_data[3]
        structural_info = line_data[4]

        corpus_name = corpus_info[0]
        cpos_start = corpus_info[1]
        cpos_end = corpus_info[2]

        chapter = structural_info[0] if len(structural_info) > 0 else None
        paragraph = structural_info[1] if len(structural_info) > 1 else None
        sentence = structural_info[2] if len(structural_info) > 2 else None

        metadata_entry = {
            'line_id': line_id,
            'text_id': corpus_name,
            'chapter': chapter,
            'paragraph': paragraph,
            'sentence': sentence
        }
        metadata_list.append(metadata_entry)

        id_in_line = 0

        def process_context(context_data, context_type):
            nonlocal id_in_line, global_token_id
            context_items = context_data[:-1]
            offsets_info = context_data[-1]
            context_str = ''.join(context_items)
            split_tokens = token_pattern.findall(context_str)
            tokens_list = [t for t in split_tokens if t.strip() != '' and not re.match(r'\s', t)]
            num_tokens = len(tokens_list)
            if context_type == 'left':
                offsets_list = list(range(-num_tokens, 0))
            elif context_type == 'node':
                offsets_list = [0] * num_tokens
            elif context_type == 'right':
                offsets_list = list(range(1, num_tokens + 1))
            else:
                raise ValueError("Invalid context_type.")
            tokens_result = []
            for tok, off in zip(tokens_list, offsets_list):
                token_entry = {
                    'id': global_token_id,
                    'id_in_line': id_in_line,
                    'line_id': line_id,
                    'offset': off,
                    'word': tok
                }
                tokens_result.append(token_entry)
                id_in_line += 1
                global_token_id += 1
            return tokens_result

        left_tokens = process_context(left_context, 'left')
        node_tokens = process_context(node, 'node')
        right_tokens = process_context(right_context, 'right')

        # If the last token in the node is a punctuation mark (or a combination of punctuation),
        # move it to the right context and adjust offsets and id_in_line accordingly.
        if node_tokens and all(c in string.punctuation for c in node_tokens[-1]['word']):
            punct_token = node_tokens.pop()
            punct_token['offset'] = 1
            for token in right_tokens:
                token['offset'] += 1
                token['id_in_line'] += 1
            punct_token['id_in_line'] = 1
            right_tokens.insert(0, punct_token)

        line_tokens = left_tokens + node_tokens + right_tokens
        token_entries.extend(line_tokens)

        if node_tokens:
            match_start_id = node_tokens[0]['id']
            match_end_id = node_tokens[-1]['id']
        else:
            match_start_id = None
            match_end_id = None

        matches_entry = {
            'line_id': line_id,
            'match_start': match_start_id,
            'match_end': match_end_id,
            'slot': 0
        }
        matches_list.append(matches_entry)

    tokens_df = pd.DataFrame(token_entries)
    tokens_df.set_index('id', inplace=True)
    metadata_df = pd.DataFrame(metadata_list)
    matches_df = pd.DataFrame(matches_list)

    self.metadata = metadata_df
    self.tokens = tokens_df
    self.matches = matches_df
    self.info["query"] = query
    self.root = AnalysisTreeNode(
        id=0,
        node_type="subset",
        parent=None,
        concordance=self,
        line_count=len(self.metadata),
        label="root",
        selected_lines=list(range(len(self.metadata)))
    )
    self.node_counter = 1
