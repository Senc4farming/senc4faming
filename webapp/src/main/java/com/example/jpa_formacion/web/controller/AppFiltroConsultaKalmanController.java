package com.example.jpa_formacion.web.controller;

import com.example.jpa_formacion.config.details.SuperCustomerUserDetails;
import com.example.jpa_formacion.dto.FiltroConsultaKalmanDto;
import com.example.jpa_formacion.service.FiltroConsultaKalmanService;
import com.example.jpa_formacion.service.MenuService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.util.Optional;

@Controller
public class AppFiltroConsultaKalmanController extends AbstractController <FiltroConsultaKalmanDto> {

    private final FiltroConsultaKalmanService service;




    public AppFiltroConsultaKalmanController(MenuService menuService,
                                             FiltroConsultaKalmanService service) {
        super(menuService);
        this.service = service;

    }

    @GetMapping("/kalman/list")
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
        Integer maxelementos = 5;
        if (size.isPresent()) {
            maxelementos = size.get();
        }

        Page<FiltroConsultaKalmanDto> dtoPage =
                this.service.buscarTodosPorUsuarioId(PageRequest.of(pagina,maxelementos),userId);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(dtoPage));
        interfazConPantalla.addAttribute("lista", dtoPage);
        return "kalman/listapagina";
    }

    int forLoop(int[] numbers, int target) {
        for (int index = 0; index < numbers.length; index++) {
            if (numbers[index] == target) {
                return index;
            }
        }
        return -1;
    }

    @GetMapping ("/kalman/graphics/{band}/{idfilter}")
    public String getkalmanImg (@PathVariable("band") Integer bandnumber,
                             @PathVariable("idfilter") Integer idfilter,
                             Model interfazConPantalla) {


        logger.info("getkalman : elemento encontrado");
        Optional<FiltroConsultaKalmanDto> filtroConsultaKalmanDtoOpt = service.encuentraPorId(idfilter);
        if (filtroConsultaKalmanDtoOpt.isPresent()){
            FiltroConsultaKalmanDto filtroConsultaKalmanDto = filtroConsultaKalmanDtoOpt.get();
            //Comprobamos si existen las imagenes
            String[] bandleters = {"B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"};
            int[] bandnumbers = {1,2,3,4,5,6,7,8,81,9,10,11,12};
            //Buscamos la posiciopn de bandnumber
            Integer position = forLoop(bandnumbers,bandnumber);
            String bandleter = bandleters[position];
            String kalmanpredfilename = "kalmanpredictionfilter" + bandleter + ".png";
            String kalmansmoothingfilename = "kalmanpredictionsmoothed" + bandleter + ".png";
            String pathKalmanpredfilename = filtroConsultaKalmanDto.getPath().replace(".csv","/kanlman/images/" +
                    filtroConsultaKalmanDto.getPointid().toString()) + "/" + kalmanpredfilename ;
            String pathKalmansmoothingfilename = filtroConsultaKalmanDto.getPath().replace(".csv","/kanlman/images/" +
                    filtroConsultaKalmanDto.getPointid().toString()) + "/" + kalmansmoothingfilename ;
            //Comprobamos si existen los archivos
            String pathKalmanpredfilenameJava = pathKalmanpredfilename.replace("/app","/solovmwarewalgreen/projecto/SEN4CFARMING/api");
            String pathKalmansmoothingfilenameJava = pathKalmansmoothingfilename.replace("/app","/solovmwarewalgreen/projecto/SEN4CFARMING/api");
            //Con api
            String pathKalmanpredfilenameApi = pathKalmanpredfilename.replace("/app","");
            String pathKalmansmoothingfilenameApi = pathKalmansmoothingfilename.replace("/app","");
            File f = new File(pathKalmanpredfilenameJava);
            if(f.exists() && !f.isDirectory()) {
                // do something
                interfazConPantalla.addAttribute("kalmanpredictionfilter", pathKalmanpredfilenameApi);
            }
            File f1 = new File(pathKalmansmoothingfilenameJava);
            if(f1.exists() && !f1.isDirectory()) {
                // do something
                interfazConPantalla.addAttribute("kalmansmoothingfilename", pathKalmansmoothingfilenameApi);
            }
            //Mostramos la pantalla de ejecucion

            logger.info("getkalman gee: paso 1");
            interfazConPantalla.addAttribute("filtro", filtroConsultaKalmanDto);
            return "kalman/consultakalmanimgs";
        }
        else{
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
        }


    }

}
