package com.example.senc4farming.controller.websockets;
import com.example.senc4farming.config.authentication.AuthenticatedUsersService;
import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.websockets.PrivateMessageDto;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.controller.AbstractController;
import lombok.extern.log4j.Log4j2;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.Set;


@Controller
@Log4j2
@RequestMapping("/chat")

public class MensajeController extends AbstractController<PrivateMessageDto> {

    private final AuthenticatedUsersService authenticatedUsersService;
    protected MensajeController(MenuService menuService, AuthenticatedUsersService authenticatedUsersService) {
        super(menuService);
        this.authenticatedUsersService = authenticatedUsersService;
    }

    @GetMapping(value = {"/admin"})
    public String chatentrenador(Model model) {
        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();
        model.addAttribute("logeduser",usuario.getNombreUsuario());

        return "/chat/chatAdmin";}

    @GetMapping(value = {"/privado"})
    public String chatatletas(Model model ) {
        Usuario usuario = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario();
        model.addAttribute("logeduser",usuario.getNombreUsuario());
        return "/chat/chatPrivado";
    }
    @GetMapping(value = {"/authusers"})
    public String getAuthUsers(Model model){
        Set<String> authUsers = authenticatedUsersService.getAuthenticatedUsers();
        model.addAttribute("list",authUsers);
        return "/chat/authusers";
    }
}


