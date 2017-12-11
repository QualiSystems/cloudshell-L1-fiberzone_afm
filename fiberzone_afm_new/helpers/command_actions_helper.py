import re


class CommandActionsHelper(object):
    @staticmethod
    def parse_table(data, pattern):
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        table = []
        for record in data.split('\n'):
            matched = re.search(compiled_pattern, record.strip())
            if matched:
                table.append(re.split(r'\s+', matched.group(0)))
        return table
