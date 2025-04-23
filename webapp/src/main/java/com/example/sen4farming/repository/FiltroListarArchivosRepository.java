package com.example.sen4farming.repository;


import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.FiltroListarArchivos;
import com.example.sen4farming.model.SentinelQueryFiles;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FiltroListarArchivosRepository extends JpaRepository<FiltroListarArchivos,Integer> {

    //Definir metodo aparte
    //Definir metodo aparte
    Page<FiltroListarArchivos> findFiltroListarArchivosByUsuarioFiltro_Id(Pageable pageable, long id);
}
