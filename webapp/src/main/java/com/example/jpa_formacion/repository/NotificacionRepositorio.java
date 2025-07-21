package com.example.jpa_formacion.repository;



import com.example.jpa_formacion.model.websockets.Notificacion;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.PagingAndSortingRepository;


import java.util.List;
import java.util.Optional;


public interface NotificacionRepositorio extends JpaRepository<Notificacion, Integer> {
    Page<Notificacion> findByUserToAndEstado(Pageable pageable,String user, String estado);

    Integer countByUserToAndEstado(String user, String estado);

    Optional<Notificacion> findById(String strId);

}

