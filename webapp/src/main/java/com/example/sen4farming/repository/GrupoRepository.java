package com.example.sen4farming.repository;


import com.example.sen4farming.model.GrupoTrabajo;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GrupoRepository extends JpaRepository<GrupoTrabajo,Integer> {

    //Definir metodo aparte
}
