package com.example.jpa_formacion.service;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Path;
import java.util.stream.Stream;

import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.processing.FilerException;

public interface FilesStorageService {
    public void init() throws FilerException;

    public void save(MultipartFile file) throws IOException;

    public Resource load(String filename) throws MalformedURLException, FileNotFoundException;

    public boolean delete(String filename) throws FileNotFoundException;

    public void deleteAll();

    public Stream<Path> loadAll();
}