package com.example.senc4farming.repository;


import com.example.senc4farming.model.FiltroConsultaKalman;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FiltroConsultaKalmanRepository extends JpaRepository<FiltroConsultaKalman,Integer> {
    Page<FiltroConsultaKalman> findFiltroConsultaKalmanByUserid(Pageable pageable, long id);
}
