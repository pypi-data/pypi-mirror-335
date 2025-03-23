import os

def merge_files(destination_file: str, source_file: str, file_type: str = ''):
    """
    Merge the contents of the source_file into the destination_file.

    :param destination_file: The path of the destination file to be merged into.
    :type destination_file: str
    :param source_file: The path of the source file to be merged from.
    :type source_file: str
    :param file_type: The file type.
    :type file_type: str
    """
    if file_type == '':
        with open(destination_file, "r+") as dest_f:
            with open(source_file, "r") as src_f:
                dest_contents = dest_f.read()
                if dest_contents and dest_contents[-1] != '\n':
                    dest_f.write('\n')
                dest_f.write(src_f.read())

    if file_type in ['histogram', 'event']:
        outfile1 = open('tmp.dat', 'w')

        # Find the startiter in the source file
        with open(source_file) as fp:
            for line in fp:
                startiter = float(line[10:])
                break

        # Read the destination file and source file, and print to outfile1
        with open(destination_file) as fp:
            for line in fp:
                if line[0] == 'T':
                    iterStep = float(line[10:])
                    if iterStep < startiter and abs(iterStep - startiter) > 1e-10:
                        outfile1.write(line)
                        outfile1.flush()
                    else:
                        break
                else:
                    outfile1.write(line)
                    outfile1.flush()

        with open(source_file) as fp:
            for line in fp:
                outfile1.write(line)
                outfile1.flush()

        # Overwrite the destination file with the contents of outfile1
        with open(destination_file, "w") as dest_f:
            with open('tmp.dat', "r") as src_f:
                dest_f.write(src_f.read())

        outfile1.close()


    if file_type in ['bound', 'copy']:
        outfile1 = open('tmp.dat', 'w')

        # Find the startiter in the source file
        with open(source_file) as fp:
            for line in fp:
                if line[0] != 'T':
                    if file_type == 'bound':
                        startiter = float(line[0:line.find('\t')])
                        break
                    else:
                        startiter = float(line[0:line.find(',')])
                        break

        # Read the destination file and source file, and print to outfile1
        with open(destination_file) as fp:
            for line in fp:
                if line[0] != 'T':
                    if file_type == 'bound':
                        iterStep = float(line[0:line.find('\t')])
                    else:
                        iterStep = float(line[0:line.find(',')])
                    if iterStep < startiter and abs(iterStep - startiter) > 1e-10:
                        outfile1.write(line)
                        outfile1.flush()
                    else:
                        break
                else:
                    outfile1.write(line)
                    outfile1.flush()

        with open(source_file) as fp:
            for line in fp:
                outfile1.write(line)
                outfile1.flush()

        # Overwrite the destination file with the contents of outfile1
        with open(destination_file, "w") as dest_f:
            with open('tmp.dat', "r") as src_f:
                dest_f.write(src_f.read())

        outfile1.close()

    if file_type == 'transition':
        outfile1 = open('tmp.dat', 'w')

        # Find the startiter in the source file
        with open(source_file) as fp:
            for line in fp:
                if line[:4] == "time":
                    startiter = float(line[6:])
                    break

        # Read the destination file and source file, and print to outfile1
        with open(destination_file) as fp:
            for line in fp:
                if line[:4] == 'time':
                    iterStep = float(line[6:])
                    if iterStep < startiter and abs(iterStep - startiter) > 1e-10:
                        outfile1.write(line)
                        outfile1.flush()
                    else:
                        break
                else:
                    outfile1.write(line)
                    outfile1.flush()

        with open(source_file) as fp:
            for line in fp:
                outfile1.write(line)
                outfile1.flush()

        # Overwrite the destination file with the contents of outfile1
        with open(destination_file, "w") as dest_f:
            with open('tmp.dat', "r") as src_f:
                dest_f.write(src_f.read())

        outfile1.close()

    if os.path.exists('tmp.dat'):
        os.remove('tmp.dat')