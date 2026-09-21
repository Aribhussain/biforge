import re
from collections import defaultdict

class PiplupParser:
    def __init__(self):
        self.delimiters = r'([ \t:,=\[\]\(\)\{\}])'
        
    def tokenize(self, log_message):
        # Split log by delimiters while keeping the delimiters for reconstruction
        tokens = re.split(self.delimiters, log_message)
        return [t for t in tokens if t]

    def parse(self, raw_logs):
        if not raw_logs:
            return {"template": ""}
            
        token_matrix = [self.tokenize(log) for log in raw_logs]
        frequency_map = defaultdict(lambda: defaultdict(int))
        
        # Build token frequency distribution
        for tokens in token_matrix:
            for i, token in enumerate(tokens):
                frequency_map[i][token] += 1
                
        total_logs = len(raw_logs)
        template_tokens = []
        
        # PIPLUP Statistical Thresholding (Data-Insensitive)
        base_tokens = token_matrix[0]
        for i in range(len(base_tokens)):
            pos_dict = frequency_map[i]
            # If a token appears in the exact same position across more than 50% of the logs, 
            # it is a static template token. Otherwise, it is a variable parameter <*>.
            most_frequent_token, count = max(pos_dict.items(), key=lambda item: item[1])
            if count / total_logs > 0.50:
                template_tokens.append(most_frequent_token)
            else:
                template_tokens.append("<*>")
                
        # Clean up consecutive variables and fused delimiters
        template = "".join(template_tokens)
        template = re.sub(r'(<\*>)+', '<*>', template)
        return {"template": template.strip()}