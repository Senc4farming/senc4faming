package com.example.senc4farming.repository;

import com.example.senc4farming.model.Mensaje;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository

public interface MensajeRepositorio extends JpaRepository<Mensaje, Integer> {
}

