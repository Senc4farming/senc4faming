package com.example.senc4farming.repository;


import com.example.senc4farming.model.GrupoTrabajo;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GrupoRepository extends JpaRepository<GrupoTrabajo,Integer> {

    //Definir metodo aparte
}
