package com.example.sen4farming.util;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.apache.commons.io.FileUtils;

/**
 * Slightly modified version of https://www.mkyong.com/java/how-to-decompress-files-from-a-zip-file/
 * @author Pedro Coelho
 */
public class Unzip {

    private final File input;
    private List<File> output = new ArrayList();
    private String outputFolder = "C:\\KMZ_TEMP";

    public Unzip(File file) {
        this.input = file;
    }

    /**
     * Sets the output TEMP folder for the unzipped files.
     * <p>
     * @param outputFolder path for the folder.
     */
    public void setOutputFolder(String outputFolder) {
        this.outputFolder = outputFolder;
    }

    /**
     * Gets files inside the ZIP input.
     * <p>
     * @return
     */
    public List<File> getOutput() {
        return output;
    }

    /**
     * Method to unzip the input file.
     * <p>
     * @param zipFile input zip file
     * @throws java.lang.Exception
     */
    public void unZipIt() throws Exception {

        byte[] buffer = new byte[1024];

        try{

            //create output directory is not exists
            File folder = new File(outputFolder);
            if(!folder.exists()){
                folder.mkdir();
            }

            //get the zipped file list entry
            try ( //get the zip file content
                  ZipInputStream zis = new ZipInputStream(new FileInputStream(input))
            ) {

                //get the zipped file list entry
                ZipEntry ze = zis.getNextEntry();

                while(ze != null){

                    String fileName = ze.getName();
                    File newFile = new File(outputFolder + File.separator + fileName);

                    //create all non existings folders
                    //else you will hit FileNotFoundException for compressed folder
                    new File(newFile.getParent()).mkdirs();

                    try (FileOutputStream fos = new FileOutputStream(newFile)) {
                        int len;
                        while ((len = zis.read(buffer)) > 0) {
                            fos.write(buffer, 0, len);
                        }
                    }

                    output.add(newFile);

                    ze = zis.getNextEntry();
                }

                zis.closeEntry();
            }

        }catch(IOException ex){
            throw(ex);
        }
    }

    /**
     * Method to delete the output folder.
     * <p>
     * Use it after reading the contents of the zip file if they were meant to be temporary.
     * @return boolean indicating if the cleaning operation was successful
     */
    public boolean clean() {

        try {
            FileUtils.deleteDirectory(new File(outputFolder));

            return true;
        } catch (Exception e) {
            return false;
        }

    }

}