package com.example.sen4farming.config.service;



import com.example.jpa_formacion.model.Usuario;
import org.springframework.stereotype.Service;



/**
 * The interface User service.
 */
@Service
public interface UserService {
    /**
     * Save user.
     *
     * @param usuario model
     */
    public String getEncodedPassword(Usuario usuario);
}
