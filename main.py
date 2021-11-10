from PyPDF4.merger import PdfFileReader, PdfFileWriter, PdfFileMerger
import re
import os


class PDFspliter:
    def __init__(self, input_path: str, output_path: str, split_string: str = None):
        self.read_path = input_path
        self.write_path = output_path
        self.splits = []
        self.split_string = split_string
        self.reg_expr = r"([\D\d\w\W]*[\\\/]).*\..*"
        self.num_created_pdfs = 0
        self.verbose = 'D'

        self.create_folder_if_missing()
        self.create_tuples()
        # print(self.splits)
        self.split_and_save_pds()

    def create_folder_if_missing(self):
        folders = re.split(r"[\\\/]", self.write_path)
        path = ".."
        for folder in folders:
            path += "/" + folder
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
            s = re.findall(r"(\d+-*\d*)", s)
            if len(s) > 1:
                if self.verbose == 'D':
                    print("[WARNING] got more indices than expected, maybe you forgot a ','. ignoring the second half")
                    print(s)
            if len(s) == 0:
                if self.verbose == 'D':
                    print("[WARNING] found no indices, skipping this one")
            else:
                s = s[0]
                if '-' in s:
                    # range
                    splitd = s.split('-')
                    i_left = int(splitd[0])
                    i_right = int(splitd[1])

                    if i_left > i_right:
                        if self.verbose == 'D':
                            print(f"[ERROR] got a range with a starting number small than the end: {i_left} > {i_right}")
                    else:
                        tpl = tuple([l for l in range(i_left, i_right+1)])
                        self.splits.append(tpl)
                else:
                    self.splits.append(tuple([int(s)]))




    def split_and_save_pds(self):
        file = PdfFileReader(self.read_path)
        num_pages = file.numPages

        for tuple in self.splits:
            path = self.new_out_file()
            # with open(path, 'w') as file_m:
            merger = PdfFileMerger()
            merger.append(fileobj=file, pages=tuple)
            merger.write(path)
            merger.close()


    def new_out_file(self):
        path = self.write_path + "/" + str(self.num_created_pdfs) + ".pdf"
        self.num_created_pdfs += 1
        return path

if __name__ == '__main__':
    # PDFspliter("Elements_of_Machine_Learning (2).pdf", "out/two", [(1), (2, 3), (4), (5, 6)])
    PDFspliter("Elements_of_Machine_Learning (2).pdf", "out/two", "1, 2-3, 4, 5-6")
"""
split pdf.pdf [(1), (2, 3), (4), (5)] => single page pdf : page 1, 4, 5
                        => multiple page pdf: page 2-3
                        
split "pdf.pdf" "1,2-3,4,5" => single page pdf : page 1, 4, 5
                            => multiple page pdf: page 2-3
"""