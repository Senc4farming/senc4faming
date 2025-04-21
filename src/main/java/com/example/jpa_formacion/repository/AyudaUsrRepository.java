package com.example.jpa_formacion.repository;


import com.example.jpa_formacion.model.AyudaUsr;
import com.example.jpa_formacion.model.Menu;
import com.example.jpa_formacion.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface AyudaUsrRepository extends JpaRepository<AyudaUsr, Integer> {

    Optional<AyudaUsr> findAyudaUsrByUrl(String url);

}
