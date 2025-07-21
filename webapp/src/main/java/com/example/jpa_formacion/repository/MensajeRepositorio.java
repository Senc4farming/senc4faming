package com.example.jpa_formacion.repository;

import com.example.jpa_formacion.model.Mensaje;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository

public interface MensajeRepositorio extends JpaRepository<Mensaje, Integer> {
}

