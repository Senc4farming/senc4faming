package com.example.sen4farming.config.service;


import com.example.jpa_formacion.model.Usuario;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * The type User service.
 */
@Service
public class UserServiceImpl implements UserService {




    private final  BCryptPasswordEncoder passwordEncoder;

    public UserServiceImpl( BCryptPasswordEncoder passwordEncoder) {

        this.passwordEncoder = passwordEncoder;
    }


    @Override
    public String getEncodedPassword(Usuario usuario) {
        String passwd = usuario.getPassword();
        return passwordEncoder.encode(passwd);
    }
}