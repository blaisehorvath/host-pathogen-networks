__author__ = 'blaise'

# parsing arguments
import argparse

parser = argparse.ArgumentParser(description='Convert downloaded RNA files to Mitab SQLite')
parser.add_argument('--source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the csv that was saved from arn")
parser.add_argument('--outfile', required=True, metavar="OutputFile", type=str,
                    help="The name and optionally location where the data should be saved.")
parser.add_argument('--db-name', required=True, metavar="DatabaseName", type=str,
                    help="The name of the source database")
parser.add_argument('--psimisql', required=True, metavar="PsimiSQLLocation", type=str,
                    help="The location of the PsimiSQL class")

args = parser.parse_args()

# imports
import sys

sys.path.append(args.psimisql)
from sqlite_db_api import PsimiSQL

# initiating the memory db
db_api = PsimiSQL()