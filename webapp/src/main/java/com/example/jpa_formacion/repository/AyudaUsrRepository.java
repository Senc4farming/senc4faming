package com.example.jpa_formacion.repository;


import com.example.jpa_formacion.model.AyudaUsr;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface AyudaUsrRepository extends JpaRepository<AyudaUsr, Integer> {

    Optional<AyudaUsr> findAyudaUsrByUrl(String url);

}
