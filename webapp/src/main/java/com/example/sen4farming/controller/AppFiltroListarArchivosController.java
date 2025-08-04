package com.example.sen4farming.web.controller;

import com.example.jpa_formacion.config.details.SuperCustomerUserDetails;
import com.example.jpa_formacion.dto.FiltroListarArchivosDto;
import com.example.jpa_formacion.service.FiltroListarArchivosService;
import com.example.jpa_formacion.service.MenuService;
import jakarta.servlet.http.HttpSession;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@Controller
public class AppFiltroListarArchivosController extends AbstractController <FiltroListarArchivosDto> {

    private final FiltroListarArchivosService service;


    private static final String STR_DET_NO_ENCONTRADO = "filtrolistararchivos/detallesnoencontrado";
    public AppFiltroListarArchivosController(MenuService menuService, FiltroListarArchivosService service) {
        super(menuService);
        this.service = service;
    }

    @GetMapping("/filtrolistararchivos")
    public String vistapagina(@RequestParam("page") Optional<Integer> page,
                                @RequestParam("size") Optional<Integer> size,
                                    ModelMap interfazConPantalla,
                              HttpSession session){
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        //Check if credentials exists
        String sessionKeycliid = "clienteid";
        Object cliId = session.getAttribute(sessionKeycliid);
        logger.info("En GetMapping /filtrolistararchivos");
        if (cliId != null){
            logger.info("Existen datos de la cookie : %s" ,cliId);

        }

        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }

        Page<FiltroListarArchivosDto> dtoPage =
                this.service.buscarTodosPorFiltroId(PageRequest.of(pagina,maxelementos),userId);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(dtoPage));
        interfazConPantalla.addAttribute("lista", dtoPage);
        return "filtrolistararchivos/listapagina";
    }
    @GetMapping("/filtrolistararchivos/{idusr}/delete")
    public String eliminarDatos(@PathVariable("idusr") Integer id){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<FiltroListarArchivosDto> dto = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (dto.isPresent()){
            this.service.eliminarPorId(id);
            //Mostrar listado de usuarios
            return "redirect:/filtrolistararchivos";
        } else{
            //Mostrar página usuario no existe
            return STR_DET_NO_ENCONTRADO;
        }
    }
    @GetMapping("/filtrolistararchivos/{idusr}")
    public String vistaDatos(@PathVariable("idusr") Integer id, ModelMap interfazConPantalla){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<FiltroListarArchivosDto> dto = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (dto.isPresent()){
            //Como encontré datos, obtengo el objerto de tipo "UsuarioDto"
            //addAttribute y thymeleaf no  entienden Optional
            FiltroListarArchivosDto attr = dto.get();
            //Asigno atributos y muestro
            interfazConPantalla.addAttribute("datos",attr);

            return "filtrolistararchivos/edit";
        } else{
            //Mostrar página usuario no existe
            return STR_DET_NO_ENCONTRADO;
        }
    }
    @GetMapping("/filtrolistararchivos/{idusr}/relanzar")
    public String vistaDatosRelanzar(@PathVariable("idusr") Integer id, ModelMap interfazConPantalla){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<FiltroListarArchivosDto> dto = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (dto.isPresent()){
            //Como encontré datos, obtengo el objerto de tipo "UsuarioDto"
            //addAttribute y thymeleaf no  entienden Optional
            FiltroListarArchivosDto attr = dto.get();
            //Asigno atributos y muestro
            interfazConPantalla.addAttribute("datos",attr);

            return "filtrolistararchivos/relaunch";
        } else{
            //Mostrar página usuario no existe
            return STR_DET_NO_ENCONTRADO;
        }
    }





}
