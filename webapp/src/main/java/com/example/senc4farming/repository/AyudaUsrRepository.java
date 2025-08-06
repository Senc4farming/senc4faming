package com.example.senc4farming.repository;


import com.example.senc4farming.model.AyudaUsr;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface AyudaUsrRepository extends JpaRepository<AyudaUsr, Integer> {

    Optional<AyudaUsr> findAyudaUsrByUrl(String url);

}
