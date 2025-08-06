package com.example.senc4farming.webapp.controller;


import com.example.senc4farming.config.authentication.AuthenticatedUsersService;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.RoleService;
import com.example.senc4farming.service.UsuarioService;
import com.example.senc4farming.service.UsuarioServiceFacade;
import com.example.senc4farming.controller.AppUsuariosController;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;


import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Test para el controlador HomeController
 */
@ExtendWith(MockitoExtension.class)
class HomeControllerTest {
    @Mock
    private UsuarioServiceFacade service;
    @Mock
    private AuthenticatedUsersService authenticatedUsersService;

    @Mock
    private MenuService menuService;

    @Mock
    private UsuarioService usuarioService;


    @Mock
    private RoleService roleService;
    @Mock
    private Model model;

    @InjectMocks
    private AppUsuariosController homeController;

    private Usuario usuario;

    private ModelMap interfazConPantalla;

    @BeforeEach
    void setUp() {
        usuario = new Usuario();
        usuario.setId(99999);
        usuario.setNombreUsuario("Usuario 99999");
        usuario.setEmail("99999@test.com");
        usuario.setActive(true);
        usuario.setRoles(roleService.buscarEntidadesSet());
    }

    @Test
    void testConstructor() {
        // Arrange & Act
        AppUsuariosController controller = new AppUsuariosController(menuService,service, authenticatedUsersService);
        
        // Assert
        assertNotNull(controller);
    }

    @Test
    void testHome() {
        String viewName = homeController.vistaHome(interfazConPantalla);
        
        assertEquals("redirect:/", viewName);
    }

}