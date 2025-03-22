import argparse

ParseOnlineBlast_usage = '''
===================== ParseOnlineBlast example commands =====================

BioSAK ParseOnlineBlast -i XXX-Alignment.txt -o XXX-Alignment_formatted.txt

# How to get the input file
On the top of the blast result page (the RID row), click "Download All", 
then choose "Text" on the top of the pop-up.

=============================================================================
'''


def ParseOnlineBlast(args):

    blast_op_txt     = args['i']
    blast_op_txt_fmt = args['o']
    top_hit_num      = args['n']

    query_to_hits_dict = dict()
    current_query = ''
    current_query_len = 0
    keep_line = 0
    wrote_line_num = 0
    blast_op_txt_fmt_handle = open(blast_op_txt_fmt, 'w')
    for each_line in open(blast_op_txt):
        each_line_split = each_line.strip().split()

        # get current_query and current_query_len
        if (each_line.startswith('Query #')) and ('Query ID:' in each_line):
            current_query = each_line.strip().split(' Query ID: ')[0].split(':')[1].strip()
            current_query_len = each_line.strip().split(' Length: ')[1]
            wrote_line_num = 0
            blast_op_txt_fmt_handle.write('\n')

        # decide to keep current line or not
        if each_line_split == ['Description', 'Name', 'Name', 'Taxid', 'Score', 'Score', 'cover', 'Value', 'Ident', 'Len', 'Accession']:
            keep_line = 1
        if len(each_line.strip()) == 0:
            keep_line = 0

        # write out
        if keep_line == 1:
            if wrote_line_num <= top_hit_num:
                blast_op_txt_fmt_handle.write('%s\t%s\t%s\n' % (current_query, each_line.strip(), current_query_len))
                wrote_line_num += 1

            # add to dict
            if each_line_split != ['Description', 'Name', 'Name', 'Taxid', 'Score', 'Score', 'cover', 'Value', 'Ident', 'Len', 'Accession']:
                if current_query not in query_to_hits_dict:
                    query_to_hits_dict[current_query] = []
                if len(query_to_hits_dict[current_query]) < top_hit_num:
                    query_to_hits_dict[current_query].append(each_line.strip())
    blast_op_txt_fmt_handle.close()


if __name__ == '__main__':

    ParseOnlineBlast_parser = argparse.ArgumentParser(usage=ParseOnlineBlast_usage)
    ParseOnlineBlast_parser.add_argument('-i',  required=True,                      help='input file')
    ParseOnlineBlast_parser.add_argument('-o',  required=True,                      help='output file')
    ParseOnlineBlast_parser.add_argument('-n',  required=True,type=int, default=20, help='top hits to keep, default is 20')
    args = vars(ParseOnlineBlast_parser.parse_args())
    ParseOnlineBlast(args)
