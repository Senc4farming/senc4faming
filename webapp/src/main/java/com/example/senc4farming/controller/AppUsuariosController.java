package com.example.senc4farming.controller;

import com.example.senc4farming.config.authentication.AuthenticatedUsersService;
import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.*;

import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.service.*;

import jakarta.mail.MessagingException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort.Order;
import org.springframework.security.access.prepost.PostAuthorize;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.AuthenticationException;

import org.springframework.security.core.context.SecurityContextHolder;

import org.springframework.security.web.WebAttributes;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.*;
import java.util.Locale;
import java.util.ResourceBundle;


import java.util.*;

@Controller
public class AppUsuariosController extends AbstractController <UsuarioDto> {

    private final  UsuarioServiceFacade service;

    private final AuthenticatedUsersService authenticatedUsersService;

    public AppUsuariosController(MenuService menuService, UsuarioServiceFacade service, AuthenticatedUsersService authenticatedUsersService) {
        super(menuService);
        this.service = service;
        this.authenticatedUsersService = authenticatedUsersService;
    }
    @GetMapping("/")
    public String vistaHome( ModelMap interfazConPantalla){

        String  userName = "no informado";
        logger.info(SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }

        interfazConPantalla.addAttribute("menuList", this.menuService.getMenuForEmail(userName));
        return "index";
    }
    @GetMapping("/privacy")
    public String vistaPrivacy( ModelMap interfazConPantalla){

        String  userName = "no informado";
        logger.info(SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }

        interfazConPantalla.addAttribute("menuList", this.menuService.getMenuForEmail(userName));
        return "privacy";
    }
    @GetMapping("/termsandconditions")
    public String vistaTermAndConditions( ModelMap interfazConPantalla){

        String  userName = "no informado";
        logger.info(SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }
        interfazConPantalla.addAttribute("menuList", this.menuService.getMenuForEmail(userName));
        return "termsandconditions";
    }
    @GetMapping("/project")
    public String vistaProject( ModelMap interfazConPantalla){

        String  userName = "no informado";
        logger.info(SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }
        interfazConPantalla.addAttribute("menuList", this.menuService.getMenuForEmail(userName));
        return "projectoeuropeo";
    }
    @GetMapping("/usuarios")
    public String vistaUsuarios(@RequestParam("page") Optional<Integer> page,
                                @RequestParam("size") Optional<Integer> size,
                                    ModelMap interfazConPantalla){


        //tenemos que leer la lista de usuarios
        //Que elemento me la ofrece?
        //listaUsrTodos
        //List<UsuarioDto>  lusrdto = this.service.listaUsrTodos();
        //interfazConPantalla.addAttribute("listausuarios", lusrdto);
        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }
        Page<UsuarioDto> usuarioDtoPage =
                this.service.getService().buscarTodos(PageRequest.of(pagina,maxelementos));


        logger.info("Elementos encontrados en vistaUsuarios");
        logger.info(usuarioDtoPage);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(usuarioDtoPage));
        interfazConPantalla.addAttribute("listausuarios", usuarioDtoPage);
        return "usuarios/listausuariospagina";
    }

    @GetMapping("/usuariossort")
    public String vistaUsuariosSort(@RequestParam("page") Optional<Integer> page,
                                @RequestParam("size") Optional<Integer> size,
                                @RequestParam(required = false) String keyword,
                                @RequestParam(defaultValue = "id,asc") String[] sort  ,
                                ModelMap interfazConPantalla){

        // para la ordenacion
        String sortField = sort[0];
        String sortDirection = sort[1];

        Direction direction = sortDirection.equals("desc") ? Sort.Direction.DESC : Sort.Direction.ASC;
        Order order = new Order(direction, sortField);



        //tenemos que leer la lista de usuarios
        //Que elemento me la ofrece?
        //listaUsrTodos
        //List<UsuarioDto>  lusrdto = this.service.listaUsrTodos();
        //interfazConPantalla.addAttribute("listausuarios", lusrdto);
        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }

        //Page<UsuarioDto> usuarioDtoPage =
        //        this.service.buscarTodos(PageRequest.of(pagina,maxelementos,Sort.by(order)));

        //Ahora las claves
        Page<UsuarioDto> usuarioDtoPage;
        if (keyword == null) {
            usuarioDtoPage = this.service.getService().buscarTodos(PageRequest.of(pagina,maxelementos,Sort.by(order)));
        } else {
            String newkeyword = "%"+ keyword + "%";
            //filtrar por el valor que se me pasa
            usuarioDtoPage =  this.service.getService().buscarTodosPorEmail(PageRequest.of(pagina,maxelementos,Sort.by(order)),newkeyword);
        }

        logger.info("Elementos encontrados en vistaUsuarios");
        logger.info(usuarioDtoPage);
        interfazConPantalla.addAttribute("currentPage", usuarioDtoPage.getNumber() + 1);
        interfazConPantalla.addAttribute("totalItems", usuarioDtoPage.getTotalElements());
        interfazConPantalla.addAttribute("totalPages", usuarioDtoPage.getTotalPages());
        interfazConPantalla.addAttribute("keyword", keyword);
        interfazConPantalla.addAttribute("pageSize", maxelementos);
        interfazConPantalla.addAttribute("sortField", sortField);
        interfazConPantalla.addAttribute("sortDirection", sortDirection);
        interfazConPantalla.addAttribute("reverseSortDirection", sortDirection.equals("asc") ? "desc" : "asc");
        interfazConPantalla.addAttribute("listausuarios", usuarioDtoPage);
        return "usuarios/listausuariospaginasort";
    }

    @GetMapping("/usuarios/{idusr}")
    @PostAuthorize("hasRole('ADMIN')")
    public String vistaDatosUsuario(@PathVariable("idusr") Integer id, ModelMap interfazConPantalla){

        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UsuarioDto> usuarioDto = this.service.getService().encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (usuarioDto.isPresent()){
            //Como encontré datos, obtengo el objerto de tipo "UsuarioDto"
            //addAttribute y thymeleaf no  entienden Optional
            UsuarioDto attr = usuarioDto.get();
            //Asigno atributos y muestro
            interfazConPantalla.addAttribute("datosUsuario",attr);

            return "usuarios/edit";
        } else{
            //Mostrar página usuario no existe
            return "usuarios/detallesusuarionoencontrado";
        }
    }


    @PostMapping("/usuarios/{idusr}/delete")
    @PreAuthorize("hasRole('ADMIN')")
    public String eliminarDatosUsuario(@PathVariable("idusr") Integer id){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UsuarioDto> usuarioDto = this.service.getService().encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (usuarioDto.isPresent()){
            this.service.getService().eliminarPorId(id);
            //Mostrar listado de usuarios
            return "redirect:/usuarios";
        } else{
            //Mostrar página usuario no existe
            return "usuarios/detallesusuarionoencontrado";
        }
    }
    @PostMapping("/usuarios/{idusr}/habilitar")
    @PreAuthorize("hasRole('ADMIN')")
    public String habilitarDatosUsuario(@PathVariable("idusr") Integer id ){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<Usuario> usuario = this.service.getService().encuentraPorIdEntity(id);
        //¿Debería comprobar si hay datos?
        if (usuario.isPresent()){
            Usuario attr = usuario.get();
            if (attr.isActive())
                attr.setActive(false);
            else
                attr.setActive(true);
            this.service.getService().getRepo().save(attr);
            //Mostrar listado de usuarios
            return "redirect:/usuarios";
        } else{
            //Mostrar página usuario no existe
            return "usuarios/detallesusuarionoencontrado";
        }
    }


    //Me falta un postmaping para guardar
    @PostMapping("/usuarios/{idusr}")
    public String guardarEdicionDatosUsuario(@PathVariable("idusr") Integer id, UsuarioDto usuarioDtoEntrada) throws Exception {
        //Cuidado que la password no viene
        //Necesitamos copiar la información que llega menos la password
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UsuarioDto> usuarioDtoControl = this.service.getService().encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (usuarioDtoControl.isPresent()){
            //LLamo al método del servicioi para guardar los datos
            UsuarioDto usuarioDtoGuardar =  new UsuarioDto();
            usuarioDtoGuardar.setId(id);
            usuarioDtoGuardar.setEmail(usuarioDtoEntrada.getEmail());
            usuarioDtoGuardar.setNombreUsuario(usuarioDtoEntrada.getNombreUsuario());
            //Obtenemos la password del sercio
            Optional<Usuario> usuario = service.getService().encuentraPorIdEntity((int) usuarioDtoGuardar.getId());
            if(usuario.isPresent()){
                this.service.getService().guardar(usuarioDtoGuardar,usuario.get().getPassword());
            }
            else {
                this.service.getService().guardar(usuarioDtoGuardar);
            }
            return String.format("redirect:/usuarios/%s", id);
        } else {
            //Mostrar página usuario no existe
            return "usuarios/detallesusuarionoencontrado";
        }
    }

    //Controlador de Login
    @GetMapping("/usuarios/login")
    public String vistaLogin(){
        return "usuarios/login";
    }
    @PostMapping("/usuarios/login")
    public String validarPasswordPst(@ModelAttribute(name = "loginForm" ) LoginDto loginDto) {
        String usr = loginDto.getUsername();
        logger.info("usr :" + usr);
        String password = loginDto.getPassword();
        logger.info("pass :" + password);
        //¿es correcta la password?
        if (service.getService().getRepo().repValidarPassword(usr, service.getPasswordEncoder().encode(password) ) > 0)
        {
            return "index";
        }else {
            return "usuarios/login";
        }
    }

    //Controlador de Login
    @GetMapping("/usuarios/hasOlvidadoTuPassword")
    public String  hasOlvidadoTuPassword(@RequestParam(value = "email", required = false) String email) throws MessagingException {

        if (email!= null) {

            Optional<Usuario> usuario = service.getService().getRepo().findUsuarioByEmailAndActiveTrue(email);

            if (usuario.isPresent()) {
                String token = usuario.get().getToken();
                logger.info("------------------------- --------------"+ email + " token: "  + token);

                Email correoCambioContrasenia = new Email();
                correoCambioContrasenia.setFrom("notificaciones@agestturnos.es");
                correoCambioContrasenia.setTo(email);
                correoCambioContrasenia.setSubject("WALGREEN change password request");
                correoCambioContrasenia.setContent("Click url to change password http://localhost:8092/usuarios/resetpass/" + email +"/" + token);

                service.getEmailService().sendMail(correoCambioContrasenia);

            } else {
                email=null;
                return "redirect:/usuarios/hasOlvidadoTuPassword";
            }

            return "usuarios/emailEnviadoParaCambioPass";
        }
        return "usuarios/hasolvidado";
    }

    // Controlador para Reset password o ¿Has olvidado tu contraseña?
    @GetMapping("/usuarios/resetpass/{email}/{token}")
    public String cambiopass(@PathVariable("email") String email, @PathVariable("token") String token, ModelMap intefrazConPantalla) {
        Optional<Usuario> usuario = service.getService().getRepo().findUsuarioByEmailAndTokenAndActiveTrue(email,token );
        logger.info(email + ":" + token );
        UsuarioDtoPsw usuarioCambioPsw = new UsuarioDtoPsw();

        if (usuario.isPresent()){
            usuarioCambioPsw.setEmail(usuario.get().getEmail());
            usuarioCambioPsw.setPassword("******************");
            usuarioCambioPsw.setNewpassword("******************");
            intefrazConPantalla.addAttribute("datos", usuarioCambioPsw);
            return "usuarios/resetearpasswordlogin";
        }else {

            //Mostrar página usuario no existe
            return "usuarios/detallesusuarionoencontrado";
        }
    }

    @PostMapping("/usuarios/resetpass")
    public String saveListaUsuariuos(@ModelAttribute  UsuarioDtoPsw  dto,
                                     @ModelAttribute UsuarioDto usuarioDTO,
                                     @RequestParam(value = "lang", required = false) String lang,
                                     Model model) throws Exception {
        String language = "en";
        if (lang!= null) {
            language = lang;
        }
        var locale = new Locale(language);
        var messages = ResourceBundle.getBundle("messages", locale);
        //Si las password no coinciden a la pag de error
        if (dto.getPassword().equals(dto.getNewpassword())){
            //Buscamnos el usuario
            Usuario usuario = service.getService().getRepo().findByEmailAndActiveTrue(dto.getEmail());
            //Actualizo la password despues de codificarla
            usuario.setPassword(service.getPasswordEncoder().encode(dto.getPassword()));
            //Cambiar tambien el token
            String tokenNuevo = UUID.randomUUID().toString();
            usuario.setToken(tokenNuevo);
            //Guardo el usuario
            Usuario usuarioguarado = service.getService().guardarEntidadEntidad(usuario);

            Email correoCambioContrasenia = new Email();
            correoCambioContrasenia.setFrom(messages.getString("principal.email.from"));
            correoCambioContrasenia.setTo(usuarioDTO.getEmail());
            correoCambioContrasenia.setSubject(messages.getString("principal.email.subject1"));
            correoCambioContrasenia.setContent(messages.getString("principal.email.content1") + usuarioDTO.getEmail() );

            service.getEmailService().sendMail(correoCambioContrasenia);

            return "redirect:/login";
        }else {

            /// Si las pass no coinciden
            //model.addAttribute("error", true);
            //return "/resetpass";
            return "usuarios/resetearpasswordlogin";

        }
    }


    //Controlador de cambio de password
    @GetMapping("/usuarios/cambiopass")
    public String vistaCambiopasword( ModelMap intefrazConPantalla){
        CambioPswDto cambioPswDto = new CambioPswDto();
        intefrazConPantalla.addAttribute("datos", cambioPswDto);
        return "usuarios/cambiopassword";
    }
    @PostMapping("/usuarios/cambiopass")
    public String cambioPasswordPst(@ModelAttribute(name="datos")CambioPswDto cambioPswDto) throws Exception {
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();

        Optional<Usuario> usuario = service.getService().encuentraPorIdEntity(userId);
        if (usuario.isPresent()){
            Usuario usuariomod = usuario.get();
            //Encriptamos las passwords
            logger.info("/usuarios/cambiopass ant:" + cambioPswDto.getPasswordant() + "---- Nueva:" + cambioPswDto.getPasswordnueva() );
            String passwordAnt =  service.getPasswordEncoder().encode(cambioPswDto.getPasswordant());
            String passwordNueva =  service.getPasswordEncoder().encode(cambioPswDto.getPasswordnueva());
            logger.info("/usuarios/cambiopass ant:" + passwordAnt );
            //Modificicamos la passsword
            usuariomod.setPassword(passwordNueva);
            logger.info("/usuarios/cambiopass antes de guardar ");
            //Guardamos el usuario
            Usuario usuario1 = service.getService().guardarEntidadEntidad(usuariomod);
            return "redirect:/logout";
        }
        else {
            return "usuarios/cambiopassword";
        }

    }
    @GetMapping("/logout/msg")
    public String logout(Model model) {
        authenticatedUsersService.removeAuthenticatedUser();
        return "usuarios/logout";
    }

    @GetMapping("/login-error")
    public String login(HttpServletRequest request, Model model) {
        HttpSession session = request.getSession(false);
        String errorMessage = null;
        if (session != null) {
            AuthenticationException ex = (AuthenticationException) session
                    .getAttribute(  WebAttributes.AUTHENTICATION_EXCEPTION);
            if (ex != null) {
                errorMessage = ex.getMessage() ;
            }
        }
        model.addAttribute("errorMessage", errorMessage);
        return "usuarios/login";
    }


}
