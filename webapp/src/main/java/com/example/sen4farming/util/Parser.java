package com.example.sen4farming.util;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.RandomAccessFile;
import java.util.Arrays;
import java.util.List;

/**
 *
 * @author Pedro Coelho
 */
public class Parser {

    private final File file;
    private FileType type;

    /**
     * 0x504B0304, 0x504B0506, 0x504B050 are 3 possible file signatures (Magic Numbers) for the ZIP format.
     **/
    final List validKMZsignatures = Arrays.asList(0x504B0304, 0x504B0506, 0x504B050);

    public enum FileType {
        KMZ("kmz"), KML("kml");

        private final String ext;
        FileType(String ext) { this.ext = ext; }

        public String getExt() { return ext; }

    }

    /**
     * Constructor for parser.
     * <p>
     * @param file file to be parsed.
     * @throws Exception If file doesn't exist, can't be parsed or unzipped.
     */
    public Parser(File file) throws Exception {
        this.file = file;

        detectFileType(file);
    }

    /**
     * Method to detect the type of a file
     * <p>
     * Utilizes the Files class implementation of the FileTypeDetector probeContentType method to determine the type of a file.
     * If this method fails, it falls back to assuming the type from the extension (UNSAFE).
     * <p>
     * Returns null on error.
     * @param file - file to be analyzed
     * @return String - String representation of the file type
     */
    private void detectFileType(File file) throws Exception {

        if (file.getTotalSpace() == 0)
            throw(new Exception("File does not exist!"));

        if (file.getName().toLowerCase().endsWith(".kmz") && checkKMZ())
            type = FileType.KMZ;
        else if (file.getName().toLowerCase().endsWith(".kml") && checkKML(file))
            type = FileType.KML;
        else
            throw(new Exception("Unsupported file type! This library only accepts KMZ and KML files."));

    }

    /**
     * Checks if file is of the KML type.
     * <p>
     * @param file file to be checked
     * @return boolean indicating if it is a KML file
     * @throws Exception
     */
    private boolean checkKML(File file) throws Exception {
        try(
                BufferedReader br = new BufferedReader(new FileReader(file));
        ) {

            String line = br.readLine();

            String line2 = br.readLine();

            return line.contains("xml") && line2.contains("kml");
        }
    }

    /**
     * Checks if file is of the KMZ type.
     * <p>
     * @return boolean indicating if it is a KMZ file
     * @throws Exception
     */
    private boolean checkKMZ() throws Exception {

        try( RandomAccessFile raf = new RandomAccessFile(file, "r"); ) {

            Integer n = raf.readInt();

            return (validKMZsignatures.contains(n));
        }
    }

    /**
     * TODO change return type and add to javadoc
     * parses the file
     */
    public void parse() throws Exception {

        switch(type) {

            case KMZ:
                parseKMZ();
                break;
            case KML:
                parseKML(file);
                break;
            default:
                // Unreachable case: Constructor throws error for unsupported formats.
                // Adding this to be safe if someone reuses this code.
                throw(new Exception("Unknown Type"));
        }

    }

    /**
     * Unzips the KMZ file and then parses the KML file inside it.
     */
    private void parseKMZ() throws Exception {

        Unzip unzip = new Unzip(file);
        unzip.unZipIt();

        for (File f : unzip.getOutput()) {
            if (f.getName().toLowerCase().endsWith(".kml") && checkKML(f))
                parseKML(f);
        }

        unzip.clean();
    }

    /**
     * TODO update with output coordinates
     * @param file
     */
    private void parseKML(File file) {

        // TODO parse XML
        System.out.println(file.getName());

    }

    /**
     * Returns the type of the file passed to the Parser class.
     * @return file type (KMZ or KML).
     */
    public FileType getType() {
        return type;
    }



}
