package com.example.senc4farming.repository;


import com.example.senc4farming.model.FiltroListarArchivos;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FiltroListarArchivosRepository extends JpaRepository<FiltroListarArchivos,Integer> {

    //Definir metodo aparte
    //Definir metodo aparte
    Page<FiltroListarArchivos> findFiltroListarArchivosByUsuarioFiltro_Id(Pageable pageable, long id);
}
