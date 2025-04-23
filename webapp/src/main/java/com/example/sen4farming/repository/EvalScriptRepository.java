package com.example.sen4farming.repository;


import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.GrupoTrabajo;
import com.example.sen4farming.model.SentinelQueryFiles;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EvalScriptRepository extends JpaRepository<EvalScript,Integer> {

    //Definir metodo aparte
    Page<EvalScript> findEvalScriptByUsuarioScript_Id(Pageable pageable, long id);
}
