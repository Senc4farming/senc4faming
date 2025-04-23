package com.example.sen4farming.web.controller;

import com.example.sen4farming.config.details.SuperCustomerUserDetails;
import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.EvalScriptLaunchDto;
import com.example.sen4farming.dto.FiltroConsultaKalmanDto;
import com.example.sen4farming.model.Usuario;
import com.example.sen4farming.service.EvalScriptService;
import com.example.sen4farming.service.FiltroConsultaKalmanService;
import com.example.sen4farming.service.MenuService;
import com.example.sen4farming.service.UsuarioService;
import jakarta.persistence.criteria.CriteriaBuilder;
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

    private final UsuarioService usuarioService;


    public AppFiltroConsultaKalmanController(MenuService menuService, FiltroConsultaKalmanService service, UsuarioService usuarioService) {
        super(menuService);
        this.service = service;
        this.usuarioService = usuarioService;
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
                             Model interfazConPantalla) throws Exception {


        System.out.println("getkalman : elemento encontrado");
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
            String path_kalmanpredfilename = filtroConsultaKalmanDto.getPath().replace(".csv","/kanlman/images/" +
                    filtroConsultaKalmanDto.getPointid().toString()) + "/" + kalmanpredfilename ;
            String path_kalmansmoothingfilename = filtroConsultaKalmanDto.getPath().replace(".csv","/kanlman/images/" +
                    filtroConsultaKalmanDto.getPointid().toString()) + "/" + kalmansmoothingfilename ;
            //Comprobamos si existen los archivos
            String path_kalmanpredfilename_java = path_kalmanpredfilename.replace("/app","/solovmwarewalgreen/projecto/SEN4CFARMING/api");
            String path_kalmansmoothingfilename_java = path_kalmansmoothingfilename.replace("/app","/solovmwarewalgreen/projecto/SEN4CFARMING/api");
            //Con api
            String path_kalmanpredfilename_api = path_kalmanpredfilename.replace("/app","");
            String path_kalmansmoothingfilename_api = path_kalmansmoothingfilename.replace("/app","");
            File f = new File(path_kalmanpredfilename_java);
            if(f.exists() && !f.isDirectory()) {
                // do something
                interfazConPantalla.addAttribute("kalmanpredictionfilter", path_kalmanpredfilename_api);
            }
            File f1 = new File(path_kalmansmoothingfilename_java);
            if(f.exists() && !f.isDirectory()) {
                // do something
                interfazConPantalla.addAttribute("kalmansmoothingfilename", path_kalmansmoothingfilename_api);
            }
            //Mostramos la pantalla de ejecucion

            System.out.println("getkalman gee: paso 1");
            interfazConPantalla.addAttribute("filtro", filtroConsultaKalmanDto);
            return "kalman/consultakalmanimgs";
        }
        else{
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
        }


    }

}
