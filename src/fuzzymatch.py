# fuzzymatch.py - Suggests approximate matches of strings against a table of
# options. 
# 
# The idea is to take as input a CSV file of (ID, STRING) pairs which forms the
# possible matches. Another table in the same format is read. Each line in this
# second table is matched against the options represented in the first table.
import cmdline, csv, sys, json
from Levenshtein import ratio, matching_blocks, editops
from argparse import FileType
from operator import itemgetter

class FuzzyMatchResult(object):
    def __init__(self, data_id, data, ratio, common_substrings):
        """
        Creates a FuzzyMatchResult.
        
        @param data_id The ID of the data string this match corresponds to
        @param data The value of this data string
        @param ratio A measure of similarity between the data and query strings.
               The value is in the interval [0, 1]
        @param common_substrings A list of (data_offset, query_offset, string) 
               tuples containing
               the substrings shared between the data string and the query
        """
        self.data_id = data_id
        self.data = data
        self.ratio = ratio
        self.common_substrings = common_substrings

class FuzzyMatcher(object):
    def __init__(self, index_str_pairs):
        self._data = index_str_pairs
    
    def match(self, query, result_count=5):
        # Get the closest n matches. Note: if this turns out to be too slow, 
        # it's possible that filtering out data unable to effect the result with
        # real_quick_ratio()/quick_ratio() would be faster. 
        sorted_matches = self._build_match_list(query)[0:result_count]
        sorted_matches = filter(lambda match: match[0] > 0, sorted_matches)
        return self._build_match_results(query, sorted_matches)
    
    def _build_match_results(self, query, matches):
        return [self._finish_match(query, match) for match in matches]
    
    def _finish_match(self, query, (ratio, data_id, data)):
        blocks = matching_blocks(editops(data, query), len(data), len(query))
        common_substrings = [(d, q, data[d:d+l])
                             for (d, q, l) in blocks if l > 0]
        return FuzzyMatchResult(data_id, data, ratio, common_substrings)
    
    def _build_match_list(self, query):
        # Build a list of tuples containing the similarity ratio ([0, 1])
        ranked = [(ratio(d, query), d_id, d)
                  for (d_id, d) in self._data]
        # Sort the results by ratio (descending)
        ranked.sort(key=itemgetter(0), reverse=True)
        return ranked

class JsonOutput(object):
    def __init__(self, dest=sys.stdout):
        self._dest = dest
        self._matches = []
    
    def output(self, query_id, query, matches):
        match = {
            "query": query,
            "query_id": query_id,
            "matches": [{"id": m.data_id, 
                         "data": m.data, 
                         "ratio": m.ratio, 
                         "common_substrings": [{"data_index": di, 
                                                "src_index": si, 
                                                "string": substr} 
                                               for [di, si, substr] 
                                               in m.common_substrings]}
                        for m in matches]
        }
        self._matches.append(match)
    
    def finish(self):
        json.dump(self._matches, self._dest, indent=4)

class CsvOutput(object):
    def __init__(self, dest=sys.stdout):
        self._writer = csv.writer(dest, 'excel')
        
    def output(self, query_id, query, matches):
        self._writer.writerow(['query', query_id, query])
        for match in matches:
            row = ['match', match.data_id, match.data, match.ratio, None]
            row = row + reduce(lambda a, b: a + list(b), 
                               match.common_substrings, [])
            self._writer.writerow(row)
        self._writer.writerow([])
    
    def finish(self):
        pass

class FuzzyMatchApp(cmdline.CmdLineApp):
    
    @staticmethod
    def _int_gt_0(val):
        res = int(val)
        if res <= 0: raise ValueError("Value was <= 0: {}".format(res))
        return res
    
    def define_arguments(self, parser):
        parser.add_argument("data_file", metavar="DATA_FILE", type=FileType("r"))
        parser.add_argument("query_file", metavar="QUERY_FILE", type=FileType("r"))
        parser.add_argument("--max-matches", "-m", type=self._int_gt_0, default=5, dest="max_matches")
        parser.add_argument("-t", "--out-type", type=str, choices={"csv", "json"}, 
                            default="csv", dest="out_type", 
                            help="The output format to use. Default: csv")
    
    @staticmethod
    def _get_output(type, dest):
        if type == "csv":
            return CsvOutput(dest=dest)
        elif type == "json":
            return JsonOutput(dest=dest)
        raise ValueError("Unknown output type: {}".format(type))
    
    def main(self, args):
        matcher = FuzzyMatcher(self.load_id_vaues(args.data_file))
        queries = self.load_id_vaues(args.query_file)
        output = self._get_output(args.out_type, dest=sys.stdout)
        
        for (query_id, query) in queries:
            matches = matcher.match(query, result_count=args.max_matches)
            output.output(query_id, query, matches)
        output.finish()
    
    def load_id_vaues(self, csv_lines):
        return [(id, value) for id, value in csv.reader(csv_lines, 'excel')]
