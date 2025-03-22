import argparse

taxdump_usage = '''
===================== taxdump example commands =====================

BioSAK taxdump -node nodes.dmp -name names.dmp -o ncbi_taxonomy.txt

# Input files available at:
https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz

====================================================================
'''

def parse_taxdump(nodes_dmp, names_dmp):

    id_to_name_dict = dict()
    for each_node in open(names_dmp):
        each_node_split = each_node.strip().split('|')
        node_id    = int(each_node_split[0].strip())
        node_name  = each_node_split[1].strip()
        name_class = each_node_split[3].strip()
        if name_class == 'scientific name':
            id_to_name_dict[node_id] = node_name

    genus_set = set()
    child_to_parent_dict = dict()
    for each_node in open(nodes_dmp):
        each_node_split = each_node.strip().split('|')
        tax_id = int(each_node_split[0].strip())
        parent_tax_id = int(each_node_split[1].strip())
        tax_rank = each_node_split[2].strip()
        child_to_parent_dict[tax_id] = parent_tax_id
        if tax_rank == 'genus':
            genus_set.add(tax_id)

    genus_lineage_dict_id = dict()
    genus_lineage_dict_name = dict()
    for genus_id in sorted(list(genus_set)):

        current_genus_id   = genus_id
        current_genus_name = id_to_name_dict[current_genus_id]

        genus_lineage_list_id = [genus_id]
        while genus_id != 1:
            genus_id = child_to_parent_dict[genus_id]
            genus_lineage_list_id.append(genus_id)

        genus_lineage_list_name = [id_to_name_dict[i] for i in genus_lineage_list_id]

        genus_lineage_str_id   = ';'.join([str(i) for i in genus_lineage_list_id[::-1]])
        genus_lineage_str_name = ';'.join(genus_lineage_list_name[::-1])

        genus_lineage_dict_id[current_genus_id] = genus_lineage_str_id
        genus_lineage_dict_name[current_genus_name] = genus_lineage_str_name

    return genus_lineage_dict_id, genus_lineage_dict_name


def taxdump(args):

    nodes_dmp   = args['node']
    names_dmp   = args['name']
    op_txt      = args['o']

    _, lineage_dict_by_name = parse_taxdump(nodes_dmp, names_dmp)

    op_txt_handle = open(op_txt, 'w')
    for genus in lineage_dict_by_name:
        genus_lineage = lineage_dict_by_name[genus]
        op_txt_handle.write('%s\t%s\n' % (genus, genus_lineage))
    op_txt_handle.close()


if __name__ == '__main__':

    taxdump_parser = argparse.ArgumentParser(usage=taxdump_usage)
    taxdump_parser.add_argument('-node',  required=True,    help='nodes.dmp')
    taxdump_parser.add_argument('-name',  required=True,    help='names.dmp')
    taxdump_parser.add_argument('-o',     required=True,    help='output file')
    args = vars(taxdump_parser.parse_args())
    taxdump(args)
