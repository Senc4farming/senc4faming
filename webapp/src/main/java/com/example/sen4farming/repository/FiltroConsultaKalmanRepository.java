package com.example.sen4farming.repository;


import com.example.sen4farming.model.FiltroConsultaKalman;
import com.example.sen4farming.model.FiltroListarArchivos;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FiltroConsultaKalmanRepository extends JpaRepository<FiltroConsultaKalman,Integer> {
    Page<FiltroConsultaKalman> findFiltroConsultaKalmanByUserid(Pageable pageable, long id);
}
