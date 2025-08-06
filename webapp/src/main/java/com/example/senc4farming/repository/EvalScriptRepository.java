package com.example.senc4farming.repository;


import com.example.senc4farming.model.EvalScript;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EvalScriptRepository extends JpaRepository<EvalScript,Integer> {

    //Definir metodo aparte
    Page<EvalScript> findEvalScriptByUsuarioScript_Id(Pageable pageable, long id);
}
