package com.example.senc4farming.config;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;

import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.io.IOException;

import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.model.shared.SessionData;
import com.example.senc4farming.service.UsuarioService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;


import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;


/**
 * Test para CustomAuthenticationSuccessHandler.
 * 
 * @author UBU
 */
@ExtendWith(MockitoExtension.class)
class CustomAuthenticationSuccessHandlerTest {

    @Mock
    private UsuarioService usuarioService;

    @Mock
    private SessionData sessionData;

    @Mock
    private HttpServletRequest request;
    
    @Mock
    private HttpServletResponse response;
    
    @Mock
    private Authentication authentication;
    
    @Mock
    private UserDetails userDetails;
    
    @InjectMocks
    private CustomAuthenticationSuccessHandler successHandler;
    
    private Usuario usuario;
    
    @BeforeEach
    void setUp() {
        usuario = new Usuario();
        usuario.setId(99999);
        usuario.setEmail("test@test.com");
        usuario.setNombreUsuario("Nombre test");
    }
    
    /**
     * Test del constructor.
     * Verifica que se inyectan correctamente las dependencias.
     */
    @Test
    void testConstructor() {
        // When
        CustomAuthenticationSuccessHandler handler = new CustomAuthenticationSuccessHandler(sessionData, usuarioService);
        
        // Then
        assertNotNull(handler);
    }
    
    /**
     * Test del constructor con parámetros null.
     * Verifica que se pueden inyectar dependencias null.
     */
    @Test
    void testConstructorWithNullParams() {
        // When
        CustomAuthenticationSuccessHandler handler = new CustomAuthenticationSuccessHandler(null, null);
        
        // Then
        assertNotNull(handler);
    }
    
    /**
     * Test de onAuthenticationSuccess con usuario encontrado.
     * Verifica que se establece correctamente el usuario en SessionData.
     */
    @Test
    void testOnAuthenticationSuccessWithUserFound() throws IOException, ServletException {
        // Given
        Integer  userId = 99999;
        String username = usuarioService.getRepo().getReferenceById (userId).getEmail();
        when(authentication.getName()).thenReturn(username);
        when(usuarioService.getRepo().getReferenceById (userId)).thenReturn(usuario);
        // When
        successHandler.onAuthenticationSuccess(request, response, authentication);

        // Then
        verify(usuarioService).getRepo().getReferenceById (userId);
        verify(sessionData).setUsuario(usuario);
        verify(response).sendRedirect("/");
    }
    
    /**
     * Test de onAuthenticationSuccess con usuario no encontrado.
     * Verifica que se maneja correctamente cuando el usuario no existe.
     */
    @Test
    void testOnAuthenticationSuccessWithUserNotFound() throws IOException, ServletException {
        // Given
        Integer  userId = 999991;
        String username = "nonExistentUser";
        when(authentication.getName()).thenReturn(username);
        when(usuarioService.getRepo().getReferenceById (userId)).thenReturn(null);
        
        // When
        successHandler.onAuthenticationSuccess(request, response, authentication);
        
        // Then
        verify(usuarioService).getRepo().getReferenceById (userId);
        verify(sessionData, never()).setUsuario(any());
        verify(response).sendRedirect("/");
    }
    

    /**
     * Test de onAuthenticationSuccess con authentication null.
     * Verifica el comportamiento con parámetros null.
     */
    @Test
    void testOnAuthenticationSuccessWithNullAuthentication() {
        // When & Then
        assertThrows(NullPointerException.class, () -> {
            successHandler.onAuthenticationSuccess(request, response, null);
        });
    }
    
    /**
     * Test de onAuthenticationSuccess con response null.
     * Verifica el comportamiento con response null.
     */
    @Test
    void testOnAuthenticationSuccessWithNullResponse() {
        // Given
        when(authentication.getName()).thenReturn("testUser");
        
        // When & Then
        assertThrows(NullPointerException.class, () -> {
            successHandler.onAuthenticationSuccess(request, null, authentication);
        });
    }
}