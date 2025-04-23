package com.example.sen4farming.repository;


import com.example.sen4farming.model.AyudaUsr;
import com.example.sen4farming.model.Menu;
import com.example.sen4farming.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface AyudaUsrRepository extends JpaRepository<AyudaUsr, Integer> {

    Optional<AyudaUsr> findAyudaUsrByUrl(String url);

}
