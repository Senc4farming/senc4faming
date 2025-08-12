package com.example.senc4farming.controller;


import com.example.senc4farming.config.ConfiguationProperties;
import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.SentinelQueryFilesTiffDto;
import com.example.senc4farming.model.SentinelQueryFilesTiff;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.SentinelQueryFilesTiffService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.*;

import java.io.*;
import java.net.URL;
import java.util.List;
import java.util.Optional;

@Controller
public class AppSentinelQueryFilesTiffController extends AbstractController <SentinelQueryFilesTiffDto> {

    private final SentinelQueryFilesTiffService service;

    private final ConfiguationProperties configuationProperties;

    private static final String STR_LISTA = "lista";
    private static final String STR_LISTA_PAGINA ="sentinelqueryfilestiff/listapagina";
    private static final String STR_NO_ENCONTRADO ="sentinelqueryfilestiff/detallesnoencontrado";

    public AppSentinelQueryFilesTiffController(MenuService menuService,
                                               SentinelQueryFilesTiffService service
                                               ,ConfiguationProperties configuationProperties) {
        super(menuService);
        this.service = service;
        this.configuationProperties = configuationProperties;
    }
    @GetMapping("/sentinelqueryfilestiff/filter/{idquery}")
    public String vistapaginafiltroGet(@RequestParam("page") Optional<Integer> page,
                                       @RequestParam("size") Optional<Integer> size,
                                       @PathVariable("idquery") Integer id,
                                       ModelMap interfazConPantalla){
        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }
        //comprobamos sio ya se han descargadoç
        List<SentinelQueryFilesTiff> sentinelQueryFilesTiffList = this.service.getRepo().findSentinelQueryFilesTiffBySentinelQueryFilesfortiff_IdAndPathLike(id,"%.tiff");
        if (!sentinelQueryFilesTiffList.isEmpty()) {
            Page<SentinelQueryFilesTiffDto> dtoPage =
                    this.service.buscarTodosPorFiltroId(PageRequest.of(pagina, maxelementos), id);
            interfazConPantalla.addAttribute("query_id", id);
            interfazConPantalla.addAttribute(pageNumbersAttributeKey, dameNumPaginas(dtoPage));
            interfazConPantalla.addAttribute(STR_LISTA, dtoPage);

            return STR_LISTA_PAGINA;
        } else {
            return String.format("redirect:/api/listfiles/downloadbands/%s", id);
        }
    }

    @PostMapping("/sentinelqueryfilestiff/filter/{idfilter}")
    public String vistapaginafiltro(@RequestParam("page") Optional<Integer> page,
                                    @RequestParam("size") Optional<Integer> size,
                                    @PathVariable("idfilter") Integer id,
                              ModelMap interfazConPantalla){
        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }
        //comprobamos sio ya se han descargadoç
        logger.info("post id en la llamada a vistapaginafiltro:" ) ;
        List<SentinelQueryFilesTiff> sentinelQueryFilesTiffList = this.service.getRepo().findSentinelQueryFilesTiffBySentinelQueryFilesfortiff_IdAndPathLike(id,"%.tiff");
        if (!sentinelQueryFilesTiffList.isEmpty() ) {
            Page<SentinelQueryFilesTiffDto> dtoPage =
                    this.service.buscarTodosPorFiltroId(PageRequest.of(pagina, maxelementos), id);
            interfazConPantalla.addAttribute("query_id", id);
            interfazConPantalla.addAttribute(pageNumbersAttributeKey, dameNumPaginas(dtoPage));
            interfazConPantalla.addAttribute(STR_LISTA, dtoPage);

            return STR_LISTA_PAGINA;
        } else {
            logger.info("post id en la llamada a vistapaginafiltro: descargamos datos no encontrados"  ) ;
            return String.format("redirect:/api/listfiles/downloadbands/%s", id);
        }
    }

    @GetMapping("/sentinelqueryfilestiff")
    public String vistapagina(@RequestParam("page") Optional<Integer> page,
                              @RequestParam("size") Optional<Integer> size,
                              ModelMap interfazConPantalla){

        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();

        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }

        Page<SentinelQueryFilesTiffDto> dtoPage =
                this.service.buscarTodosPorFiltroId(PageRequest.of(pagina, maxelementos),userId);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey, dameNumPaginas(dtoPage));
        interfazConPantalla.addAttribute(STR_LISTA, dtoPage);

        return STR_LISTA_PAGINA;
    }


    @PostMapping("/sentinelqueryfilestiff/{idusr}/delete")
    public String eliminarDatos(@PathVariable("idusr") Integer id){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<SentinelQueryFilesTiffDto> dto = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (dto.isPresent()){
            this.service.eliminarPorId(id);
            //Mostrar listado de usuarios
            return "redirect:/sentinelqueryfilestiff";
        } else{
            //Mostrar página usuario no existe
            return STR_NO_ENCONTRADO;
        }
    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @GetMapping("/sentinelqueryfilestiff/show/{idfile}/{idprev}")
    public String showFileGet(@PathVariable("idfile") Integer id,
                           @PathVariable("idprev") Integer idprev,
                           Model interfazConPantalla)  {
        logger.info("/sentinelqueryfilestiff/show/ get");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);

        if (sentinelQueryFilesTiffDto.isPresent()) {
            return String.format("redirect:/visor/image/map/%s/%s", id,idprev);
        } else {
            //Mostrar página usuario no existe
            return STR_NO_ENCONTRADO;
        }
    }


    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/sentinelqueryfilestiff/show/{idfile}/{idprev}")
    public String showFile(@PathVariable("idfile") Integer id,
                           @PathVariable("idprev") Integer idprev,
                                 Model interfazConPantalla)  {
        logger.info("/sentinelqueryfilestiff/show/ post");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);

        if (sentinelQueryFilesTiffDto.isPresent()) {
            return String.format("redirect:/visor/image/map/%s/%s", id,idprev);
        } else {
            //Mostrar página usuario no existe
            return STR_NO_ENCONTRADO;
        }
    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @GetMapping("/sentinelqueryfilestiff/show/tiff/{idfile}/{idprev}")
    public String showFileGetTiff(@PathVariable("idfile") Integer id,
                              @PathVariable("idprev") Integer idprev,
                              Model interfazConPantalla)  {
        logger.info("/sentinelqueryfilestiff/show/tiff/ get");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);

        if (sentinelQueryFilesTiffDto.isPresent()) {
            return String.format("redirect:/visor/image/%s/%s", id,idprev);
        } else {
            //Mostrar página usuario no existe
            return STR_NO_ENCONTRADO;
        }
    }


    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/sentinelqueryfilestiff/show/tiff/{idfile}/{idprev}")
    public String showFileTiff(@PathVariable("idfile") Integer id,
                           @PathVariable("idprev") Integer idprev,
                           Model interfazConPantalla) {
        logger.info("/sentinelqueryfilestiff/show/tiff/ post");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);

        if (sentinelQueryFilesTiffDto.isPresent()) {
            return String.format("redirect:/visor/image/%s/%s", id,idprev);
        } else {
            //Mostrar página usuario no existe
            return STR_NO_ENCONTRADO;
        }
    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @GetMapping("/sentinelqueryfilestiff/show/test")
    public String showFiletest(
                           Model interfazConPantalla) throws IOException {
        String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/tiff/1951/jma_burgos_10009/212/tiff/s2l2a/07/eaeae90dca5418433feb1eda081bb544/response.tiff";


        URL url = new URL(urltext);


        InputStream is = url.openStream();
        try (OutputStream os = new FileOutputStream("response.tiff")) {

            byte[] b = new byte[2048];
            int length;

            while ((length = is.read(b)) != -1) {
                os.write(b, 0, length);
            }
        } finally {
            is.close();
        }
        return STR_NO_ENCONTRADO;
    }

}