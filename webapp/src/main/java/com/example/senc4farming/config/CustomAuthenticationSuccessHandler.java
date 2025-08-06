package com.example.senc4farming.config;

import java.io.IOException;
import java.util.Optional;

import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.model.shared.SessionData;
import com.example.senc4farming.service.UsuarioService;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;


import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Manejador personalizado para el éxito de autenticación.
 * Se encarga de establecer el usuario en SessionData cuando la autenticación es exitosa.
 *
 * @autor José Manuel Aroca
 * @version 1.0
 * @since 1.0
 */
@Component
public class CustomAuthenticationSuccessHandler implements AuthenticationSuccessHandler {

    private final SessionData sessionData;
    private final UsuarioService usuarioService;

    Logger logger = LogManager.getLogger(this.getClass());

    public CustomAuthenticationSuccessHandler(SessionData sessionData, UsuarioService usuarioService) {
        this.sessionData = sessionData;
        this.usuarioService = usuarioService;
    }

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {

        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        logger.info("Usuario autenticado exitosamente: {}", userId);

        // Buscar el usuario en la base de datos y establecerlo en SessionData
        Optional<Usuario> usuario = usuarioService.encuentraPorIdEntity(userId);
        if (usuario.isPresent()) {
            sessionData.setUsuario(usuario.get());
            logger.info("Usuario establecido en SessionData: {}", usuario.get().getNombreUsuario());
        } else {
            logger.warn("No se pudo encontrar el usuario en la base de datos: {}", userId);
        }

        // Redirigir al menú principal
        response.sendRedirect("/");
    }
}