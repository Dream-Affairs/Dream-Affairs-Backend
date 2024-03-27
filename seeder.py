"""Seed file for generating fake data to test out the import feature."""
import csv
import os
import sys
from typing import Any, Dict, List

from faker import Faker
from openpyxl import Workbook

from app.core.config import settings

SAMPLE_DIR = os.path.join(os.path.abspath(settings.SAMPLE_DIR))

DEFAULT_COUNT = 10

fake = Faker()


def generate_data(count):
    """This is the main function that populates a list which is returned."""
    generated_data = []
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        phone = fake.phone_number()
        address: str = fake.address()
        city = fake.city()
        state = fake.state()
        zip_code = fake.zipcode()
        country = fake.country()
        tags = fake.words()

        generated_data.append(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": phone,
                "address": address.replace("\n", ", "),
                "city": city,
                "state": state,
                "zip": zip_code,
                "country": country,
                #  quote tags in "[tag1, tag2, tag3]" format
                "tags": "[" + ", ".join([f"{tag}" for tag in tags]) + "]",
            }
        )

    return generated_data


def create_csv_file(generated_data, name):
    """It creates the csv file if it does not exist and write the generated
    data into  it."""
    with open(
        SAMPLE_DIR + "/" + name, "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=generated_data[0].keys())
        writer.writeheader()
        writer.writerows(generated_data)


def create_xlsx_file(generated_data: List[Dict[str, Any]], name: str) -> None:
    """This function creates/writes the generated data into the file."""
    wb: Workbook = Workbook()
    ws: Workbook.active = wb.active

    ws.append(list(generated_data[0].keys()))
    for row in generated_data:
        ws.append(list(row.values()))
    wb.save(SAMPLE_DIR + "/" + name)


# def count_csv_file_lines(filename, count):
#     with open(filename, 'r+') as file:
#         lines = file.readlines()
#         file.seek(0)
#         file.truncate()
#         file.writelines(lines[:count])

if __name__ == "__main__":
    args_len = len(sys.argv)
    if "-h" == sys.argv[1]:
        print("<fname>: This should be the name to be given to the file")
        print(
            "<filetype>: This should be the type of file to be generated\
               ('csv' or 'xlsx').It has a default of csv"
        )
        print(
            "<flines>: This is the amount of data generated.\
                  It has a default of 10"
        )
        sys.exit(0)
    if args_len < 2 or args_len > 3:
        print("Usage: python script.py <fname> <flines>")
        sys.exit(1)

    fname = sys.argv[1]
    ftype = sys.argv[2] if args_len >= 3 else "csv"
    flines = int(sys.argv[3]) if args_len > 3 else DEFAULT_COUNT
    print("Value 1:", fname)
    print("Value 2:", ftype)
    print("Value 3:", flines)

    if ftype == "csv":
        data = generate_data(flines)
        create_csv_file(data, fname)
    elif ftype == "xlsx":
        data = generate_data(flines)
        create_xlsx_file(data, fname)
    # count_csv_file_lines(fname, lines + 1)
