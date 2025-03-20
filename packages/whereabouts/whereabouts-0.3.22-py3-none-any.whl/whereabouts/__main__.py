import sys
from .utils import setup_geocoder, remove_database, download, convert_db

def main():
    if len(sys.argv) < 3:
        print("Error: invalid command\nUse one of the following commands: \nsetup_geocoder, download, remove_database, convert_database\n")
        print("Usage: \npython -m whereabouts setup_geocoder <config_file_path>")
        print("python -m whereabouts download <db_name>")
        print("python -m whereabouts remove_database <db_name>")
        print("python -m whereabouts convert_database <db_name>")
        sys.exit(1)

    command = sys.argv[1]
    if command == "setup_geocoder":
        config_path = sys.argv[2]
        setup_geocoder(config_path)
    if command == "remove_database":
        db_name = sys.argv[2]
        remove_database(db_name)
    if command == "download":
        db_name = sys.argv[2]
        download(db_name, 'saunteringcat/whereabouts-db')
    if command == "convert_database":
        db_name = sys.argv[2]
        convert_db(db_name)

if __name__ == "__main__":
    main()