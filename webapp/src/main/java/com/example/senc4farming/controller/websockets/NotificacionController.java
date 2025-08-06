package com.example.senc4farming.controller.websockets;

import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.websockets.NotificacionDto;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.model.websockets.Notificacion;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.UsuarioService;
import com.example.senc4farming.service.websockets.NotificacionService;
import com.example.senc4farming.controller.AbstractController;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.security.Principal;
import java.util.Optional;

@Controller
public class NotificacionController extends AbstractController<NotificacionDto> {


    private final UsuarioService usuarioService;

    private final NotificacionService notificacionService;

    protected NotificacionController(MenuService menuService, UsuarioService usuarioService, NotificacionService notificacionService) {
        super(menuService);
        this.usuarioService = usuarioService;
        this.notificacionService = notificacionService;
    }

    @PreAuthorize("isAuthenticated()")
    @GetMapping("/notificaciones")
    public String mostrarNotificaciones(@RequestParam("page") Optional<Integer> page,
                                        @RequestParam("size") Optional<Integer> size,
                                        ModelMap interfazConPantalla){
        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();
        interfazConPantalla.addAttribute("logeduser",usuario.getNombreUsuario());

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
        Page<NotificacionDto> notificacionDtos =
                this.notificacionService.buscarTodos(PageRequest.of(pagina,maxelementos));

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),"Pendiente");

        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(notificacionDtos));
        interfazConPantalla.addAttribute("listanotificaciones", notificacionDtos);
        interfazConPantalla.addAttribute("numpendientes",numPendientes);
        return "/notificaciones/index";
    }


    @GetMapping("/leerNotificaciones")
    public String leerNotificacionesPendientes(@RequestParam("page") Optional<Integer> page,
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

        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();
        interfazConPantalla.addAttribute("logeduser",usuario.getNombreUsuario());

        Page<NotificacionDto> notificacionDtos =
                this.notificacionService.buscarTodosEstado(PageRequest.of(pagina,maxelementos),usuario.getNombreUsuario(), "Pendiente");

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),"Pendiente");
        interfazConPantalla.addAttribute("numpendientes",numPendientes);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(notificacionDtos));
        interfazConPantalla.addAttribute("listanotificaciones", notificacionDtos);
        return "/notificaciones/index";
    }
    @GetMapping("/leerNotificacion/{id}")
    public String leerNotificacionesPendientes(@PathVariable("id") Integer id, ModelMap interfazConPantalla ) {
        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();
        interfazConPantalla.addAttribute("logeduser",usuario.getNombreUsuario());

        Optional<Notificacion> notificacion = this.notificacionService.buscar(id);

        if (notificacion.isPresent()) {
            notificacion.get().setEstado("READ");
            this.notificacionService.guardarEntidadEntidad(notificacion.get());
        }

        return "redirect:/notificaciones";
    }

    @GetMapping("/numeroNotificaciones")
    @ResponseBody
//    @PreAuthorize("isAuthenticated()")
    public String contarNotificacionesPendientes(Principal principal,Model model, Authentication authentication
    ) {
        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),"Pendiente");
        return String.valueOf(numPendientes);
    }
}
