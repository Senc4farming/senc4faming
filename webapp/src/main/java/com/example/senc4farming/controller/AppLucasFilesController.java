package com.example.senc4farming.controller;

import com.example.senc4farming.dto.SentinelQueryFilesTiffDto;
import com.example.senc4farming.service.MenuService;
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