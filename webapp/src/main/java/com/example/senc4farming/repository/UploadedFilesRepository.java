package com.example.senc4farming.repository;


import com.example.senc4farming.model.UploadedFiles;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UploadedFilesRepository extends JpaRepository<UploadedFiles,Integer> {

     Page<UploadedFiles> findUploadedFilesByUsuarioUpload_Id(Pageable pageable, long id);   //Definir metodo aparte
}
