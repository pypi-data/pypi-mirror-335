import argparse

from nosql_bulk_automation_package_tst.Generator import Generator


# workbook = xlrd.open_workbook(sys.argv[1])

# sh = workbook.sheet_by_index(0)

# for details in range(1,sh.nrows):
#     list=sh.row_values(details)
#     # Generator().parameters(list)
    
### new implementation with the compatibilty ofthe jenkisn inout for individual one ##########
datastore = "Couchbbase"
app = "ape"
paas_name = "tst-ne-cur01a"
sec_zone = "tnz"
phase = "pdt"
cid = "asc-01-a"
reg = "ne"
LZ = "amacp-tst-ne-cur-01"
size = "M"

# Generator().parameters(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size)

# Define the command-line argument parser
def parse_args():
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    
    parser.add_argument("--datastore", type=str, required=True, help="Datastore type")
    parser.add_argument("--app", type=str, required=True, help="App name")
    parser.add_argument("--paas_name", type=str, required=True, help="PAAS name")
    parser.add_argument("--sec_zone", type=str, required=True, help="Security zone")
    parser.add_argument("--phase", type=str, required=True, help="Phase")
    parser.add_argument("--cid", type=str, required=True, help="CID")
    parser.add_argument("--reg", type=str, required=True, help="Region")
    parser.add_argument("--LZ", type=str, required=True, help="LZ name")
    parser.add_argument("--size", type=str, required=True, help="Size")

    return parser.parse_args()

# Main function to run the script
def main():
    args = parse_args()
    
    # Print out the arguments to confirm
    print(f"Datastore: {args.datastore}")
    print(f"App: {args.app}")
    print(f"PAAS Name: {args.paas_name}")
    print(f"Security Zone: {args.sec_zone}")
    print(f"Phase: {args.phase}")
    print(f"CID: {args.cid}")
    print(f"Region: {args.reg}")
    print(f"LZ: {args.LZ}")
    print(f"Size: {args.size}")
    Generator().parameters(args.datastore,args.app,args.paas_name,args.sec_zone,args.phase,args.cid,args.reg,args.LZ,args.size)

# if __name__ == "__main__":
#     main()
