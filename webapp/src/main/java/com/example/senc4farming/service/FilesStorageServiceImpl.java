package com.example.senc4farming.service;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InterruptedIOException;
import java.lang.module.FindException;
import java.net.MalformedURLException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;

import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.FileSystemUtils;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.processing.FilerException;

@Service
public class FilesStorageServiceImpl implements FilesStorageService {

    private final Path root = Paths.get("./src/main/resources/static/imagenes/");

    @Override
    public void init() throws FilerException {
        try {
            Files.createDirectories(root);
        } catch (IOException e) {
            throw new FilerException("Could not initialize folder for upload!");
        }
    }

    @Override
    public void save(MultipartFile file) throws IOException {
        try {
            Files.copy(file.getInputStream(), this.root.resolve(file.getOriginalFilename()));
        } catch (FileAlreadyExistsException e) {
                throw new FileAlreadyExistsException("A file of that name already exists.");
        } catch (Exception e) {

            throw new InterruptedIOException(e.getMessage());
        }
    }

    @Override
    public Resource load(String filename) throws MalformedURLException, FileNotFoundException {
        Path file = root.resolve(filename);
        Resource resource = new UrlResource(file.toUri());

        if (resource.exists() || resource.isReadable()) {
            return resource;
        } else {
            throw new FileNotFoundException("Could not read the file!");
        }
    }

    @Override
    public boolean delete(String filename) throws FileNotFoundException {
        try {
            Path file = root.resolve(filename);
            return Files.deleteIfExists(file);
        } catch (IOException e) {
            throw new FileNotFoundException("Error: " + e.getMessage());
        }
    }

    @Override
    public void deleteAll() {
        FileSystemUtils.deleteRecursively(root.toFile());
    }

    @Override
    public Stream<Path> loadAll() {
        try {
            return Files.walk(this.root, 1).filter(path -> !path.equals(this.root)).map(this.root::relativize);
        } catch (IOException e) {
            throw new FindException("Could not load the files!");
        }
    }
}