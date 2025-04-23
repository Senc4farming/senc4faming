package com.example.sen4farming.repository;


import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.GrupoTrabajo;
import com.example.sen4farming.model.UploadedFiles;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UploadedFilesRepository extends JpaRepository<UploadedFiles,Integer> {

     Page<UploadedFiles> findUploadedFilesByUsuarioUpload_Id(Pageable pageable, long id);   //Definir metodo aparte
}
