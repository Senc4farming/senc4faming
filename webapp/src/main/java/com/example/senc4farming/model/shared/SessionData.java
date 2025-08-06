package com.example.senc4farming.model.shared;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.context.annotation.SessionScope;

import jakarta.validation.ConstraintViolationException;
import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;

/**
 * Clase SessionData que almacena la información de la sesión del usuario.
 *
 * @autor José Manuel Aroca
 * @version 1.0
 * @since 1.0
 *
 */
@Slf4j
@Getter
@Setter
@SessionScope
@Service
public class SessionData implements Serializable {

    /**
     * serialVersionUID
     */
    private static final long serialVersionUID = 927145734999089972L;

    /**
     * Inyección de UsuarioRepo
     */
    private transient UsuarioRepository usrRepo;

    /**
     * Constructor de la clase SessionData.
     * <p>
     * Constructor vacío para CDI
     */
    public SessionData() {
        // Constructor vacío para CDI
    }

    /**
     * Constructor de la clase SessionData.
     */
    @Autowired
    public SessionData(UsuarioRepository usuarioRepo) {
        this.usrRepo = usuarioRepo;
    }

    /**
     * Usuario
     */
    private Usuario usuario;



    /**
     * Usuario
     */
    private List<Integer> lstRolesUsuario = new ArrayList<>();

    /**
     * registroUsuarioEntrada
     *
     * @param userId the user id
     */
    public void registroUsuarioEntrada(Integer userId) {
        Usuario user;
        try {
            user = usrRepo.findById(userId).orElse(null);
        } catch (Exception e) {
            user = null;
            log.error("Error al buscar el usuario: " + e.getMessage());
        }
        if (Objects.nonNull(user)) {
            try {
                this.setUsuario(user);
                user.setFechaUltimoAcceso(LocalDateTime.now());
                usrRepo.save(user);
            } catch (ConstraintViolationException e) {
                log.error("Error de constraint al guardar el usuario: " + e.getMessage());
                e.getConstraintViolations().forEach(err -> log.error(err.toString()));
            } catch (Exception e) {
                log.error("Error al guardar el usuario: " + e.getMessage());
            }
        }
    }

}
