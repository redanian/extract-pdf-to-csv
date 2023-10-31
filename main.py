import os
from typing import List, Optional

from pypdf import PdfReader

FOLDER = 'INSERT FOLDER HERE'


def find_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """Find files recursively in a folder."""
    files = []

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if extension is None or filename.endswith(extension):
                full_path = os.path.abspath(os.path.join(dirpath, filename))
                files.append(full_path)

    return files


def extract_text_from_pdf(file: str) -> List[str]:
    """Extract the text from a PDF file as a list of lines."""
    return [line for page in PdfReader(file).pages for line in page.extract_text().split('\n')]


def extract_text_from_txt(file: str) -> List[str]:
    """Extract the text from a file as a list of lines."""
    with open(file, 'r', encoding='utf-8') as file_reader:
        return file_reader.readlines()


def map_pdf_to_txt(pdf_file: str) -> None:
    """Extract text from a PDF file and store it in a TXT file."""
    # Create the corresponding .txt and .txt.tmp filenames.
    txt_file = os.path.splitext(pdf_file)[0] + ".txt"
    tmp_file = txt_file + ".tmp"

    # If the .txt file already exists, skip.
    if os.path.exists(txt_file):
        return

    # Remove existing temporary file if it exists.
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    # Extract text from PDF.
    lines = extract_text_from_pdf(pdf_file)

    content = '\n'.join(lines)

    # Write content to the temporary file.
    with open(tmp_file, 'w', encoding='utf-8') as out_file:
        out_file.write(content)

    # Rename the temporary file to the final .txt file upon successful write.
    os.rename(tmp_file, txt_file)


def map_txt_to_csv(txt_file: str) -> None:
    """Extract text from a TXT file, parse it as tabular data and store it in a CSV file."""
    # Create the corresponding .csv and .csv.tmp filenames.
    csv_file = os.path.splitext(txt_file)[0] + ".csv"
    tmp_file = csv_file + '.tmp'

    # If the .csv file already exists, skip.
    if os.path.exists(csv_file):
        return

    # Remove existing temporary file if it exists.
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    lines = extract_text_from_txt(txt_file)

    # Map lines to data points and filter out empty lines (or empty rows).
    table = [row for line in lines for row in [parse_line(line, txt_file)] if row]

    # Map table to csv file content.
    csv_content = '\n'.join([','.join(map(str, row)) for row in table])

    # Write content to the temporary file.
    with open(tmp_file, 'w') as file:
        file.writelines(csv_content)

    # Rename the temporary file to the final .csv file upon successful write.
    os.rename(tmp_file, csv_file)


def parse_line(line: str, txt_file: str) -> List[str]:
    """Convert a text line in a table row."""
    # Perform custom checks and line transformations.
    # TODO add custom checks (e.g. for skipping) and line transformation logic here.

    # Check if line is still irregular, even after transformation.
    if is_line_irregular(line):
        print(f'\nCannot parse "{line}" in file "{txt_file}". Please adjust transformation logic and try again.')
        exit(1)

    # Parse line to data points.
    # TODO add line parsing logic here.
    return []


def is_line_irregular(line: str) -> bool:
    """Check if a line has an expected format."""
    # TODO add checks here.
    return True


def merge_csv_files(csv_files: List[str]) -> None:
    """All for one."""
    # Create .csv and .csv.tmp filenames.
    data_file = 'data.csv'
    tmp_file = data_file + '.tmp'

    # If the .csv file already exists, skip.
    if os.path.exists(data_file):
        return

    # Remove existing temporary file if it exists.
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    # Copy the content of all CSVs into one.
    with open(tmp_file, 'w') as outfile:
        for idx, csv in enumerate(csv_files):
            print(f'\rCopying information from CSV file {idx + 1} of {len(csv_files)}...', end='')
            outfile.writelines(extract_text_from_txt(csv))

    # Rename the temporary file to the final .csv file upon successful write.
    os.rename(tmp_file, data_file)
    print(f'\rMerged {len(csv_files)} CSV files into {data_file}.' + 50 * ' ', end='\n')


def main():
    # Extract text from PDFs to TXTs.
    pdf_files = find_files(FOLDER, extension='.pdf')
    for (idx, pdf) in enumerate(pdf_files):
        print(f'\rExtracting text from PDF file {idx + 1} of {len(pdf_files)}...', end='')
        map_pdf_to_txt(pdf)
    print(f'\rMapped {len(pdf_files)} PDF files to TXT.' + 50 * ' ', end='\n')

    # Parse data from TXTs to CSVs.
    txt_files = find_files(FOLDER, extension='.txt')
    for idx, txt in enumerate(txt_files):
        print(f'\rParsing information from TXT file {idx + 1} of {len(txt_files)}...', end='')
        map_txt_to_csv(txt)
    print(f'\rMapped {len(txt_files)} TXT files to CSV.' + 50 * ' ', end='\n')

    # Aggregate CSVs.
    csv_files = find_files(FOLDER, extension='.csv')
    merge_csv_files(csv_files)


if __name__ == '__main__':
    main()
