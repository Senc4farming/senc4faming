package com.example.sen4farming.controller.websockets;

import com.example.jpa_formacion.config.details.SuperCustomerUserDetails;
import com.example.jpa_formacion.dto.UsuarioDto;
import com.example.jpa_formacion.dto.websockets.NotificacionDto;
import com.example.jpa_formacion.model.Usuario;
import com.example.jpa_formacion.model.websockets.Notificacion;
import com.example.jpa_formacion.service.MenuService;
import com.example.jpa_formacion.service.UsuarioService;
import com.example.jpa_formacion.service.websockets.NotificacionService;
import com.example.jpa_formacion.web.controller.AbstractController;
import lombok.extern.log4j.Log4j2;
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
import java.util.List;
import java.util.Optional;

@Controller
public class NotificacionController extends AbstractController<NotificacionDto> {


    private final NotificacionService notificacionService;

    private final String strPendiente = "Pendiente";

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

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),strPendiente);

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
                this.notificacionService.buscarTodosEstado(PageRequest.of(pagina,maxelementos),usuario.getNombreUsuario(), strPendiente);

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),strPendiente);
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

        Integer numPendientes = this.notificacionService.getRepo().countByUserToAndEstado(usuario.getNombreUsuario(),strPendiente);
        return String.valueOf(numPendientes);
    }
}
