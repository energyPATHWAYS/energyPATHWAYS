#!/usr/bin/env python
from __future__ import print_function
import click
import json
import os
import shutil

from json_loader import Scenario, init_db, get_name_for_id, read_foreign_keys

def strip_suffix(s, suffix):
    return s[:-len(suffix)] if s.endswith(s) else s

@click.command()
@click.argument('json_file', type=click.Path(exists=True))      # Positional argument

@click.option('--dbname', '-d', default='pathways',
              help='PostgreSQL database name (default="pathways")')

@click.option('--host', '-h', default='localhost',
              help='Host running PostgreSQL (default="localhost")')

@click.option('--user', '-u', default='postgres',
              help='PostgreSQL user name (default="postgres")')

@click.option('--password', '-p', default='',
              help='PostreSQL password (default="")')

@click.option('--outfile', '-o', default=None,
              help='''The new JSON file to create with names substituted for IDs. \
Default is to rename the original file with a "~" appended and to write the new file \
to the same name as the input JSON file. See also: --backup/--no-backup''')

@click.option('--backup/--no-backup', default=True,
              help='''If --backup is selected, (the default) the original JSON file \
is renamed with a tilde ("~") appended before overwriting with the updated contents. \
Note that this flag is ignored when the --outfile/-o flag is used.''')

@click.option('--fix-dupes/--no-fix-dupes', default=True,
              help='''If --fix-dupes is used (the default), measures with non-unique names are have \
their integer postgres ID appended in parentheses to distinguish them; these will require manual \
correction. If --no-fix-dupes, duplicate values appear in the output JSON file.''')


def main(json_file, dbname, host, user, password, outfile, backup, fix_dupes):
    init_db(host, dbname, user, password)
    fkeys = read_foreign_keys()

    scenario = Scenario(json_file)

    outpath = outfile if outfile else json_file

    # handles case of explicit outfile that's the same as input JSON file
    if outpath == json_file and backup:
        backup_name = json_file + '~'
        try:
            os.remove(backup_name)
        except:
            pass

        shutil.copy2(json_file, json_file + '~')

    top = scenario.scenario[scenario._name]
    for case_name, case_values in top.items():

        if isinstance(case_values, dict):
            for measure_name, measure_dict in case_values.items():

                if measure_name == 'Sensitivities':
                    sens_dicts = measure_dict   # in this case, it's a list of dicts
                    for sens_dict in sens_dicts:
                        table = sens_dict['table']
                        parent_id = sens_dict['parent_id']
                        par_col = Scenario.parent_col(table)
                        fkey = fkeys.query("table_name == '{}' and column_name == '{}'".format(table, par_col))
                        if len(fkey) == 1:
                            foreign_table  = fkey['foreign_table_name'].iloc[0]
                            sens_dict['name'] = get_name_for_id(foreign_table, parent_id, fix_dupes=fix_dupes)
                            sens_dict['col_name'] = strip_suffix(par_col, '_id')
                            sens_dict['table'] = strip_suffix(table, 'Data')    # Strip trailing 'Data' from name to match merged table
                            del sens_dict['parent_id']
                else:
                    for key, values in measure_dict.items():
                        if key != 'description':
                            names = []
                            for id in values:
                                s = get_name_for_id(key, id, fix_dupes=fix_dupes)
                                if s is not None:
                                    names.append(s)
                            measure_dict[key] = names

    with open(outpath, 'w') as out:
        json.dump(scenario.scenario, out, indent=4)

if __name__ == '__main__':
    main()