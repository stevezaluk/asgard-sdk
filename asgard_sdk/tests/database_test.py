from ..connection.database import Database

def main():
    d = Database("192.168.1.220", 27017)
    d.connect()

if __name__ == "__main__":
    main()