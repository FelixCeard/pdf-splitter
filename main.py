from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import argparse


parser = argparse.ArgumentParser(description='Split a pdf file into sub files.')
parser.add_argument('')


class PDFspliter:
    def __init__(self, input_path: str, output_path: str, split_string: str = None):
        self.read_path = input_path
        self.write_path = output_path
        self.splits = []
        self.split_string = split_string
        self.reg_expr = r"([\D\d\w\W]*[\\\/]).*\..*"
        self.num_created_pdfs = 0
        self.verbose = 'D'
        self.smallest = 9999
        self.outputed_files = []

        self.fix_paths()
        self.create_folder_if_missing()
        self.create_tuples()
        # print(self.splits)
        self.split_and_save_pds()

    def create_folder_if_missing(self):
        if not re.search(r":", self.write_path):
            abs_path = os.path.abspath(".").replace("\\", '/')
            self.write_path = abs_path + self.write_path.replace("\\", '/')

        folders = re.split(r"[\\\/]", self.write_path)
        path = ""
        for folder in folders:
            path += folder + "/"
            if not os.path.exists(path):
                os.mkdir(path)

    def create_tuples(self):
        """
        get String of grammar '\d, \d, \d-\d'
        :return: A list of tuples containing the page numbers indicated by the grammar
        """
        splited = self.split_string.split(",")
        for s in splited:
            s = s.replace(" ", "")
            s = re.findall(r"^(\d+-*\d*)", s)

            if len(s) > 1:
                if self.verbose == 'D':
                    print("[WARNING] got more indices than expected, maybe you forgot a ','. ignoring the second half")
            if len(s) == 0:
                if self.verbose == 'D':
                    print("[WARNING] found no indices, skipping this one")
            else:
                s = s[0]
                if '-' in s:
                    splitd = s.split('-')
                    i_left = int(splitd[0])
                    i_right = int(splitd[1])
                    if i_left > i_right:
                        if self.verbose == 'D':
                            print(f"[ERROR] got a range with a starting number small than the end: {i_left} > {i_right}")
                    else:
                        tpl = tuple([l for l in range(i_left, i_right + 1)])
                        self.smallest = min(i_left, self.smallest)
                        self.smallest = min(i_right, self.smallest)
                        self.splits.append(tpl)
                else:
                    self.smallest = min(int(s), self.smallest)
                    self.splits.append(tuple([int(s)]))

    def split_and_save_pds(self):
        with open(self.read_path, 'rb') as rf:
            reader = PdfFileReader(rf)
            num_pages = reader.numPages

            for tuple in self.splits:
                self.check_tuple(tuple, num_pages)
                path = self.new_out_file(str(tuple))
                merger = PdfFileWriter()
                for index in tuple:
                    merger.addPage(reader.getPage(index - self.smallest))
                with open(path, 'wb') as f:
                    merger.write(f)

    def new_out_file(self, name: str):

        finds = re.findall(r"\d", name)
        name = ','.join(finds)

        path = self.write_path + "page_" + name + ".pdf"
        self.outputed_files.append(path)
        self.num_created_pdfs += 1
        return path

    def check_tuple(self, tuple, num_pages):
        for number in tuple:
            if (number < 1) or (number > num_pages):
                raise IndexError(
                    f"Expected indices inside the scope of the pdf ({num_pages} pages), so a number between (1 and {num_pages})")

    def merge_all(self):
        merger = PdfFileWriter()

        for path in self.outputed_files:
            with open(path, 'rb') as rf:
                reader = PdfFileReader(rf)
                num_pages = reader.numPages
                for i in range(num_pages):
                    merger.addPage(reader.getPage(i))

        with open(self.write_path + "merged.pdf", 'wb') as f:
            merger.write(f)

    def fix_paths(self):
        if self.write_path[-1] not in ['/', '\\']:
            self.write_path += "/"
            self.write_path.replace("\\", "/")

        if not os.path.exists(self.read_path):
            raise Exception(f"File doesnt doesn't exist: {self.read_path}")