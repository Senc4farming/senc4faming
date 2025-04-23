package com.example.sen4farming.repository;


import com.example.sen4farming.model.Menu;
import com.example.sen4farming.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface MenuRepository extends JpaRepository<Menu, Integer> {

    List<Menu> findDistinctByRolesIn(Collection<Role> roles);

    List<Menu> findDistinctByRolesInAndActiveTrue(Collection<Role> roles);

    List<Menu> findDistinctByRolesInAndActiveTrueOrderByOrder(Collection<Role> roles);

    Optional<Menu> findByUrlAndActiveTrue(String url);

    Optional<Menu> findByDescription02AndActiveTrue(String url);

}
