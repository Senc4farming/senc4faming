package com.example.sen4farming.repository;



import com.example.sen4farming.model.PythonScript;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PythonScriptRepository extends JpaRepository<PythonScript,Integer> {

    //Definir metodo aparte
    Page<PythonScript>  findPythonScriptByUsuarioPythonScript_Id(Pageable pageable, Integer id);
}
