package com.example.senc4farming.controller;

import com.example.senc4farming.config.service.UserService;
import com.example.senc4farming.dto.*;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.service.GrupoService;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.RoleService;
import com.example.senc4farming.service.UsuarioService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

import static com.example.senc4farming.util.ValidarFormatoPassword.validarformato;

@Controller
public class AppUsuariosSeguridadController extends AbstractController <UsuarioDto> {

    private final UserService userService;
    private final  UsuarioService service;


    private final RoleService roleService;

    private final GrupoService grupoService;

    private static final String STR_USUARIOS_REGISTRO ="usuarios/registro";
    private static final String STR_LISTA_ROLES ="listaRoles";

    public AppUsuariosSeguridadController(MenuService menuService,  UserService userService, UsuarioService service, RoleService roleService, GrupoService grupoService) {
        super(menuService);
        this.userService = userService;
        this.service = service;
        this.roleService = roleService;
        this.grupoService = grupoService;
    }


    // Read Form data to save into DB

    //Para crear un usuario hay dos bloques
    //El que genera la pantalla para pedir los datos de tipo GetMapping
    //Cuando pasamos informacion a la pantalla hay que usar ModelMap
    @GetMapping("/usuarios/registro")
    public String vistaRegistro(Model interfazConPantalla){
        //Obtengo la lista de roles
        final List<RoleDTO> roleDTOList = roleService.buscarTodosAlta();
        //Obtengo la lista de grupos
        final List<GrupoTrabajoDto> grupoTrabajoDtos = grupoService.buscarTodos();
        //Mediante "addAttribute" comparto con la pantalla
        interfazConPantalla.addAttribute(STR_LISTA_ROLES,roleDTOList);
        interfazConPantalla.addAttribute("listagrupos",grupoTrabajoDtos);
        logger.info("Preparando pantalla registro");
        return STR_USUARIOS_REGISTRO;
    }
    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/usuarios/registro")
    public String guardarUsuario( @ModelAttribute(name ="datosUsuario") UsuarioDtoPsw usuarioDtoPsw
            , Model model)  {
        //Obtengo la lista de roles
        final List<RoleDTO> roleDTOList = roleService.buscarTodosAlta();
        //Comprobamos el patron
        logger.info("Guardando usuario antes ");
        logger.info("Usuario :%s, password :%s ", usuarioDtoPsw.getNombreUsuario(), usuarioDtoPsw.getPassword() );
        if (validarformato(usuarioDtoPsw.getPassword())){
            Usuario usuario = service.getMapper().toEntityPsw(usuarioDtoPsw);
            logger.info("Guardando usuario");
            //Codifico la password
            String encodedPasswod = userService.getEncodedPassword(usuario);
            usuarioDtoPsw.setPassword(encodedPasswod);
            //Se anulan los grupos
            usuarioDtoPsw.setGrupoTrabajo(this.grupoService.buscarSinOpt(1));
            //El usuario se guarda como no autorizado
            //Guardo la password
            try {
                UsuarioDto usuario1 = this.service.guardar(usuarioDtoPsw);
                return String.format("redirect:/usuarios/%s", usuario1.getId());
            }
            catch (Exception ex){
                logger.info("Excepcion:%s" , ex.getMessage());
                if ( ex.getMessage().contains("idx_usuario_email"))
                {
                    model.addAttribute("errorMessage", "Email in use, use a different email.");
                    model.addAttribute(STR_LISTA_ROLES,roleDTOList);
                    return STR_USUARIOS_REGISTRO;

                }
                else
                    throw ex ;
            }

        }
        else
        {
            model.addAttribute("errorMessage", "Password format not valid");
            model.addAttribute(STR_LISTA_ROLES,roleDTOList);
            return STR_USUARIOS_REGISTRO;
        }

    }
}
