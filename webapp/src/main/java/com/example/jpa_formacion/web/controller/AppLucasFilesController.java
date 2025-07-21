package com.example.jpa_formacion.web.controller;

import com.example.jpa_formacion.config.ConfiguationProperties;
import com.example.jpa_formacion.dto.SentinelQueryFilesTiffDto;
import com.example.jpa_formacion.service.MenuService;
import com.example.jpa_formacion.service.SentinelQueryFilesTiffService;
import com.example.jpa_formacion.service.UsuarioService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;


@Controller
public class AppLucasFilesController extends AbstractController <SentinelQueryFilesTiffDto> {





    public AppLucasFilesController(MenuService menuService) {
        super(menuService);

    }
    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @GetMapping("/lucasfiles/show/{pathfile}")
    public String showFile(@PathVariable("pathfile") String path,
                                 Model interfazConPantalla)  {

       if (path.isEmpty() ){
           return "lucas/detallesimagennoencontrado";
        } else {
            //Mostrar página usuario no existe
            return String.format("redirect:/visor/image/lucas/%s", path);
        }
    }
}