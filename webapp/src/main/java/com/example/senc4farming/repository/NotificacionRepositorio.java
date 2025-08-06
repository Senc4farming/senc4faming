package com.example.senc4farming.repository;



import com.example.senc4farming.model.websockets.Notificacion;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;


import java.util.Optional;


public interface NotificacionRepositorio extends JpaRepository<Notificacion, Integer> {
    Page<Notificacion> findByUserToAndEstado(Pageable pageable,String user, String estado);

    Integer countByUserToAndEstado(String user, String estado);

    Optional<Notificacion> findById(String strId);

}

