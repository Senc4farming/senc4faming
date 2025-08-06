package com.example.senc4farming.config.service;



import com.example.senc4farming.model.Usuario;
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
