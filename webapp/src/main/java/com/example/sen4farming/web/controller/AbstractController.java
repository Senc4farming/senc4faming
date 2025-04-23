package com.example.sen4farming.web.controller;

import com.example.sen4farming.config.details.SuperCustomerUserDetails;
import com.example.sen4farming.dto.MenuDTO;
import com.example.sen4farming.model.AyudaUsr;
import com.example.sen4farming.model.Menu;
import com.example.sen4farming.model.Usuario;
import com.example.sen4farming.service.AyudaUsrService;
import com.example.sen4farming.service.MenuService;
import com.example.sen4farming.service.UsuarioService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.data.domain.Page;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;
import org.springframework.web.bind.annotation.ModelAttribute;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
//Esta clase abstracta admite cualuiertipode objeto DTO o entidad
public abstract class   AbstractController<OBJ> {

    MenuService menuService;

    UsuarioService usuarioService;

    protected AbstractController(MenuService menuService) {
        this.menuService = menuService;
        this.usuarioService = usuarioService;
    }
    //Literal para los numeros de pagina
    protected final String pageNumbersAttributeKey = "pageNumbers";
    //Metodo para obtener los numeros de pagina
    protected List<Integer> dameNumPaginas(Page<OBJ>  obj){
        List<Integer> pageNumbers = new ArrayList<>();
        int totalPages = obj.getTotalPages();
        if (totalPages > 0) {
            pageNumbers = IntStream.rangeClosed(1, totalPages)
                    .boxed()
                    .collect(Collectors.toList());
        }
        return pageNumbers;
    }
    @ModelAttribute("rutamenu")
    public String rutanavegacion(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByUrlAndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            return menu.get().getDescription01();
        }
        else{
            return("Not found");
        }
    }
    @ModelAttribute("userlogin")
    public String userlogin(HttpServletRequest request){
        //Obtenemos los datos del usuario
        String username = "Not found";
        System.out.println("User id" +   SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString() == "anonymousUser" ){
            return("Not found");
        }else {
            return  ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }
    }



    @ModelAttribute("urlmenuayuda")
    public String urlmenuayuda(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByUrlAndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            return menu.get().getDescription02();
        }
        else{
            return("Not found");
        }
    }

    @ModelAttribute("menuList")
    public List<MenuDTO> menu() {
        String  userName = "no informado";
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }
        return this.menuService.getMenuForEmail(userName);
    }

    @ModelAttribute("ayudatitulo")
    public String ayudatitulo(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByDescription02AndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            String url = menu.get().getDescription02();
            return this.menuService.ayudatitulo(url);
        }
        else{
            return("Not found");
        }
    }

    @ModelAttribute("ayudadesc")
    public String userguide(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByDescription02AndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            String url = menu.get().getDescription02();
            return this.menuService.ayudadesc(url);
        }
        else{
            return("Not found");
        }
    }

    @ModelAttribute("ayudabody")
    public String ayudabody(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByDescription02AndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            String url = menu.get().getDescription02();
            System.out.println("body");
            System.out.println(url);
            System.out.println(this.menuService.ayudabody(url));
            return this.menuService.ayudabody(url);
        }
        else{
            System.out.println("Help not present");
            return("Not found");
        }
    }

}
