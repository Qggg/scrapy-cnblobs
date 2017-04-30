import os

class WriteIntoFile:
    @classmethod
    def write_a_file(cls, filename, writecontent, autoinc = True):
        writefilename = filename
        extent_no = 0
        if autoinc:
            while os.path.exists(writefilename):
                extent_no += 1
                writefilename = filename + str(extent_no)

        Fp = open(writefilename, "wb")
        Fp.write(writecontent)
        Fp.close()