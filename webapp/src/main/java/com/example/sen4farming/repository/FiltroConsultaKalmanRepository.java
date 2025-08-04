package com.example.sen4farming.repository;


import com.example.jpa_formacion.model.FiltroConsultaKalman;
import com.example.jpa_formacion.model.FiltroListarArchivos;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FiltroConsultaKalmanRepository extends JpaRepository<FiltroConsultaKalman,Integer> {
    Page<FiltroConsultaKalman> findFiltroConsultaKalmanByUserid(Pageable pageable, long id);
}
