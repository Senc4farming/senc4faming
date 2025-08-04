package com.example.sen4farming.util;



import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class FileUploadUtil {
    static Logger logger = LogManager.getLogger(FileUploadUtil.class);

    private FileUploadUtil() {
        throw new IllegalStateException("Utility class");
    }
    public static void saveFile(String uploadDir, String fileName,
                                MultipartFile multipartFile) throws IOException {
        Path uploadPath = Paths.get(uploadDir);

        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        logger.info("saveFile: Path creado:%s", uploadDir);
        logger.info("saveFile: fileName: %s", fileName);

        try (InputStream inputStream = multipartFile.getInputStream()) {
            Path filePath = uploadPath.resolve(fileName);
            Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException ioe) {
            throw new IOException("Could not save image file: " + fileName, ioe);
        }
    }
    public static boolean checkfile(String uploadDir, String fileName){
        Path fullpath = Paths.get(uploadDir + "/" + fileName);
        return Files.exists(fullpath);

    }
}