import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 flight_delay.py <SOURCE_AIRPORT_CODE> <DESTINATION_AIRPORT_CODE>")
        quit()
    
    source_airport = sys.argv[1]
    destination_airport = sys.argv[2]

    print(f"Determining aircraft delays: {source_airport} --> {destination_airport}...")


if __name__ == "__main__":
    main()
