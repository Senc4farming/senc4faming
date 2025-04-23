package com.example.sen4farming.repository;


import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.EvalScriptLaunch;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EvalScriptLaunchRepository extends JpaRepository<EvalScriptLaunch,Integer> {

    //Definir metodo aparte
}
