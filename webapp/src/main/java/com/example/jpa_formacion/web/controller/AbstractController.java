package com.example.jpa_formacion.web.controller;


import com.example.jpa_formacion.config.details.SuperCustomerUserDetails;
import com.example.jpa_formacion.dto.MenuDTO;
import com.example.jpa_formacion.model.Menu;
import com.example.jpa_formacion.service.MenuService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.data.domain.Page;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.ModelAttribute;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.IntStream;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
//Esta clase abstracta admite cualuiertipode objeto DTO o entidad
public abstract class   AbstractController<DTO> {

    MenuService menuService;
    Logger logger = LogManager.getLogger(this.getClass());

    private String notfound = "Not found";
    //Literal para los numeros de pagina
    protected static String pageNumbersAttributeKey = "pageNumbers";
    protected AbstractController(MenuService menuService) {
        this.menuService = menuService;
    }

    //Metodo para obtener los numeros de pagina
    protected List<Integer> dameNumPaginas(Page<DTO>  obj){
        List<Integer> pageNumbers = new ArrayList<>();
        int totalPages = obj.getTotalPages();
        if (totalPages > 0) {
            pageNumbers = IntStream.rangeClosed(1, totalPages)
                    .boxed()
                    .toList();
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
            return(notfound);
        }
    }
    @ModelAttribute("userlogin")
    public String userlogin(HttpServletRequest request){
        //Obtenemos los datos del usuario
        logger.info("User id {}",SecurityContextHolder.getContext().getAuthentication().getPrincipal());
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString().equals( "anonymousUser") ){
            return(notfound);
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
            return(notfound);
        }
    }

    @ModelAttribute("menuList")
    public List<MenuDTO> menu() {
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            return this.menuService.getMenuForEmail("anonimo@anonimo");
        }
        else {
            return this.menuService.getMenuForEmail(((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername());
        }

    }

    @ModelAttribute("ayudatitulo")
    public String ayudatitulo(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByDescription02AndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            String url = menu.get().getDescription02();
            return this.menuService.ayudatitulo(url);
        }
        else{
            return(notfound);
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
            return(notfound);
        }
    }

    @ModelAttribute("ayudabody")
    public String ayudabody(HttpServletRequest request){
        Optional<Menu> menu = this.menuService.getRepo().findByDescription02AndActiveTrue(request.getRequestURI());
        if (menu.isPresent()){
            String url = menu.get().getDescription02();
            logger.info("body");
            logger.info(url);
            return this.menuService.ayudabody(url);
        }
        else{
            logger.info("Help not present");
            return(notfound);
        }
    }

}
