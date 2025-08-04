package com.example.sen4farming.web.controller;


import java.io.*;
import java.net.MalformedURLException;
import java.util.Iterator;
import java.util.Map;
import java.util.Optional;

import com.example.jpa_formacion.dto.DatosLucas2018Dto;
import com.example.jpa_formacion.dto.EvalScriptLaunchDto;
import com.example.jpa_formacion.dto.SentinelQueryFilesTiffDto;
import com.example.jpa_formacion.model.Dates;
import com.example.jpa_formacion.model.DatosLucas2018;
import com.example.jpa_formacion.service.*;

import jakarta.validation.Valid;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import org.json.simple.JSONArray;

import org.json.simple.JSONObject;

import org.json.simple.parser.*;


@Controller
public class ImageController extends AbstractController <SentinelQueryFilesTiffDto>{


    private final FilesStorageService storageService;
    private final SentinelQueryFilesTiffService service;

    private final DatosLucas2018Service datosLucas2018Service;

    private final EvalScriptLaunchService evalScriptLaunchService;

    private final DatesService datesService;
    private static final  String STR_MINLONG ="minlong";
    private static final String STR_MINLAT = "minlat";
    private static final String STR_MAXLONG = "maxlong";
    private static final String STR_MAXLAT = "maxlat";
    private static final String STR_IMAGE = "image";
    private static final String STR_POLYGON = "polygon";
    private static final String STR_MESSAGE= "message";

    private static final String STR_F_SRC= "files/src_data_safe/";

    private static final String STR_RESPONSETIFF = "/response.tiff";
    private static final String STR_REQUESTJSON = "/request.json";

    private static final String STR_API = "api/";
    private static final String STR_APP = "/app/";
    private static final String STR_IDPREV = "idprev";

    private static final String STR_V_IMAGES_PREV = "/visor/imagesprevkml";
    private static final String STR_REQUESTS ="request";
    private static final String STR_BOUNDS ="bounds";
    private static final String STR_INPUT ="input";
    private static final String STR_PAYLOAD ="payload";
    private static final String STR_USERFILES ="userfiles/";
    public ImageController(MenuService menuService, FilesStorageService storageService, SentinelQueryFilesTiffService service, DatosLucas2018Service datosLucas2018Service, EvalScriptLaunchService evalScriptLaunchService, DatesService datesService) {
        super(menuService);
        this.storageService = storageService;
        this.service = service;
        this.datosLucas2018Service = datosLucas2018Service;
        this.evalScriptLaunchService = evalScriptLaunchService;
        this.datesService = datesService;
    }

    @GetMapping("/visor/images/new")
    public String newImage(Model model) {
        return "upload_form";
    }

    @PostMapping("/visor/images/upload")
    public String uploadImage(Model model, @RequestParam("file") MultipartFile file) {
        String message = "";

        try {
            storageService.save(file);

            message = "Uploaded the image successfully: " + file.getOriginalFilename();
            model.addAttribute(STR_MESSAGE, message);
        } catch (Exception e) {
            message = "Could not upload the image: " + file.getOriginalFilename() + ". Error: " + e.getMessage();
            model.addAttribute(STR_MESSAGE, message);
        }

        return "/visor/upload_form";
    }

    @GetMapping("/visor/image/evalscript/{id}")
    public String getListImagesEvalscript(@PathVariable("id") Integer id,Model model) {
        Optional<EvalScriptLaunchDto> evalScriptLaunchDto = evalScriptLaunchService.encuentraPorId(id);
        String pathcompleto =  evalScriptLaunchDto.get().getPathtiff();

        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES)+10,(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        logger.info(" /visor/images Path: %s", internalpath );
        model.addAttribute(STR_IMAGE, internalpath);

        return "/visor/images";
    }

    @GetMapping("/visor/image/{id}")
    public String getListImages(@PathVariable("id") Integer id,Model model) throws IOException, ParseException {
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);
        String pathcompleto =  sentinelQueryFilesTiffDto.get().getPath();
        SentinelQueryFilesTiffDto sentinelQueryFilesTiffDto1 = sentinelQueryFilesTiffDto.get();
        String polygon = sentinelQueryFilesTiffDto1.getSentinelQueryFilesfortiff().getFiltroListarArchivos().getPolygon();
        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES),(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        String internalpathjson =  STR_API +uploadDir + STR_REQUESTJSON;
        logger.info("Path:");
        logger.info(internalpath);
        logger.info(polygon);
        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internalpathjson));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }

        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internalpath);
        model.addAttribute(STR_POLYGON, polygon);

        return "/visor/images";
    }
    private void logsLongLat(Number minlong, Number minlat, Number maxlong, Number maxlat  ){
        logger.info("coords minlong : %s", minlong );
        logger.info("coords minlat : %s", minlat );
        logger.info("coords  maxlong: %s", maxlong );
        logger.info("coords  maxlat : %s",  maxlat );
    }
    @GetMapping("/visor/image/{id}/{idprev}")
    public String getListImagesBack(@PathVariable("id") Integer id,
                                    @PathVariable("idprev") Integer idprev,
                                    Model model) throws IOException, ParseException {
        logger.info("getListImagesBack");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);
        String pathcompleto =  sentinelQueryFilesTiffDto.get().getPath();
        SentinelQueryFilesTiffDto sentinelQueryFilesTiffDto1 = sentinelQueryFilesTiffDto.get();
        String polygon = sentinelQueryFilesTiffDto1.getSentinelQueryFilesfortiff().getFiltroListarArchivos().getPolygon();
        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES),(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        String internalpathjson =  STR_API +uploadDir + STR_REQUESTJSON;
        logger.info("Path: /%s" ,internalpath);
        logger.info(polygon);
        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internalpathjson));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }

        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internalpath);
        model.addAttribute(STR_POLYGON, polygon);
        model.addAttribute(STR_IDPREV, idprev);

        return "/visor/imagesprevmyqueryv1";
    }
    @GetMapping("/visor/image/map/{id}/{idprev}")
    public String getListImagesMapBack(@PathVariable("id") Integer id,
                                    @PathVariable("idprev") Integer idprev,
                                    Model model) throws IOException, ParseException {
        logger.info("getListImagesMapBack");
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);
        String pathcompleto =  sentinelQueryFilesTiffDto.get().getPath();
        SentinelQueryFilesTiffDto sentinelQueryFilesTiffDto1 = sentinelQueryFilesTiffDto.get();
        String polygon = sentinelQueryFilesTiffDto1.getSentinelQueryFilesfortiff().getFiltroListarArchivos().getPolygon();
        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES),(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        String internalpathjson =  STR_API +uploadDir + STR_REQUESTJSON;
        logger.info("Path /%s" ,internalpath);
        logger.info(polygon);
        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internalpathjson));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }

        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internalpath);
        model.addAttribute(STR_POLYGON, polygon);
        model.addAttribute(STR_IDPREV, idprev);

        return "/visor/imagesprevmyqueryv1map";
    }
    @GetMapping("/visor/image/tiff/{id}/{idprev}")
    public String getListImagesTiff(@PathVariable("id") Integer id,
                                    @PathVariable("idprev") Integer idprev,
                                    Model model) throws IOException, ParseException {
        Optional<SentinelQueryFilesTiffDto> sentinelQueryFilesTiffDto = service.encuentraPorId(id);
        String pathcompleto =  sentinelQueryFilesTiffDto.get().getPath();
        SentinelQueryFilesTiffDto sentinelQueryFilesTiffDto1 = sentinelQueryFilesTiffDto.get();
        String polygon = sentinelQueryFilesTiffDto1.getSentinelQueryFilesfortiff().getFiltroListarArchivos().getPolygon();
        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES),(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        String internalpathjson =  STR_API +uploadDir + STR_REQUESTJSON;
        logger.info("Path:");
        logger.info(internalpath);
        logger.info(polygon);
        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internalpathjson));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }

        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internalpath);
        model.addAttribute(STR_POLYGON, polygon);
        model.addAttribute(STR_IDPREV, idprev);

        return "/visor/imagesgeotiff";
    }


    @GetMapping("/visor/image/lucaspoints")
    public String showlucaspoints(Model model, Dates dates)  {
        return STR_V_IMAGES_PREV;
    }

    @PostMapping("/visor/image/lucaspoints")
    public String showlucaspointsPost(Model model, @Valid Dates dates, BindingResult result)  {
        if (result.hasErrors()) {
            return STR_V_IMAGES_PREV;
        }
        logger.info(dates.getStartDate());
        long interval = datesService.calculateDateInterval(dates.getStartDate(), dates.getEndDate());
        logger.info(interval);
        return STR_V_IMAGES_PREV;
    }

    @GetMapping("/visor/image/jcpoints")
    public String showjcpoints(Model model)  {
        return "/visor/imagesprevkmljc";
    }


    @GetMapping("/visor/image/evalscriptn/{id}")
    public String getListImagesEvalscriptnew(@PathVariable("id") Integer id,Model model) throws IOException, ParseException {
        Optional<EvalScriptLaunchDto> evalScriptLaunchDto = evalScriptLaunchService.encuentraPorId(id);
        String pathcompletotiff =  evalScriptLaunchDto.get().getPathtiff();
        String pathcompletojson =  evalScriptLaunchDto.get().getPathjson();
        //Traducimos a  la imagen en local
        logger.info("Path inicial: %s" , pathcompletotiff);


        String internaltifffloat32path = pathcompletojson.replace(STR_APP,STR_API );
        //
        String internaltiffautopath = pathcompletotiff.replace(STR_APP,"");
        //¿Existe?
        File f = new File(internaltiffautopath);
        if (f.exists()){
            logger.info("internaltiffautopath  encontrado");
        }

        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internaltifffloat32path));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }


        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internaltiffautopath);
        model.addAttribute(STR_POLYGON, evalScriptLaunchDto.get().getPolygon());

        return "/visor/imagesprevmyqueryv1";
    }

    @GetMapping("/visor/image/lucas/{id}")
    public String getPathImags(@PathVariable("id") Long id,Model model) throws IOException, ParseException {
        Optional<DatosLucas2018Dto> datosLucas2018Dto = datosLucas2018Service.encuentraPorId(id);
        String pathcompleto =  datosLucas2018Dto.get().getPath();
        //Traducimos a  la imagen en local
        logger.info("Path inicial: %s" , pathcompleto);


        String internaltifffloat32path = pathcompleto.replace(STR_APP,STR_API );
        String internaljsonfloat32path = internaltifffloat32path.replace("response.tiff","request.json" );
        //Buscanmos el path para la imagen a mostrar
        //Obtenemos el id del punto y la banda
        Optional<DatosLucas2018> datosLucas2018 = datosLucas2018Service.buscar(id);
        // Con los datos buscamos los registros con auto el json y el tiff
        //Buscamos el tiff
        DatosLucas2018 datosLucas20181TiffAuto = datosLucas2018Service.getlucasreglike(
                datosLucas2018.get().getSearchid(),
                datosLucas2018.get().getPointid(),
                datosLucas2018.get().getBand(), "%AUTO%response.tiff");
        //
        String internaltiffautopath = datosLucas20181TiffAuto.getPath().replace(STR_APP,"");
        //¿Existe?
        File f = new File(internaltiffautopath);
        if (f.exists()){
            logger.info("internaltiffautopath  encontrado");
        }
        String internaljsonautopath =  internaltiffautopath.replace("response.tiff","request.json" );

        //Falta leer el json
        Object o = new JSONParser().parse(new FileReader(internaljsonfloat32path));
        JSONObject jsonObject = (JSONObject) o;
        Number minlong = 0;
        Number minlat = 0;
        Number maxlong = 0;
        Number maxlat = 0;
        if ( jsonObject.get(STR_REQUESTS) instanceof JSONObject ) {
            logger.info("lvl0");
            Object jsonrequest = jsonObject.get(STR_REQUESTS);
            JSONObject lvl1 = new JSONObject((Map) jsonrequest);
            if ( lvl1.get(STR_PAYLOAD) instanceof JSONObject ) {
                logger.info("lvl1");
                Object jsonpayload = lvl1.get(STR_PAYLOAD);
                JSONObject lvl2 = new JSONObject((Map) jsonpayload);
                if (  lvl2.get(STR_INPUT) instanceof JSONObject ) {
                    logger.info("lvl2");
                    Object jsoninput = lvl2.get(STR_INPUT);
                    JSONObject lvl3 = new JSONObject((Map) jsoninput);
                    if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                        logger.info("lvl3");
                        Object jsonbounds = lvl3.get(STR_BOUNDS);
                        JSONObject lvl4 = new JSONObject((Map) jsonbounds);
                        if (lvl3.get(STR_BOUNDS) instanceof JSONObject) {
                            logger.info("lvl4");
                            Object cc =  lvl4.get("bbox");
                            if (cc instanceof JSONArray last ) {
                                minlong = getMinMaxCoords(last,0);
                                minlat = getMinMaxCoords(last,1);
                                maxlong = getMinMaxCoords(last,2);
                                maxlat = getMinMaxCoords(last,3);
                            }

                        }
                    }
                }
            }
        }
        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        model.addAttribute(STR_POLYGON, "0");
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute("image32", internaltifffloat32path);
        model.addAttribute("imageauto", internaltiffautopath);
        model.addAttribute("json32", internaljsonfloat32path);
        model.addAttribute("jsonauto", internaljsonautopath);
        model.addAttribute(STR_IDPREV, id);

        return "/visor/imagesprevlucasv1";
    }

    private Number getMinMaxCoords(JSONArray jsonArray,Integer pos){
        Iterator i = jsonArray.iterator();
        Integer iter = 0;
        Number valRes = 0;
        while(i.hasNext()) {
            Number val = (Number) i.next();
            if ( iter.equals(pos))
                valRes = val;
            iter +=1;
        }
        return  valRes;
    }



    @GetMapping("/visor/images/{filename:.+}")
    public ResponseEntity<Resource> getImage(@PathVariable String filename) throws MalformedURLException, FileNotFoundException {
        Resource file = storageService.load(filename);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + file.getFilename() + "\"").body(file);
    }

    @GetMapping("/visor/images/delete/{filename:.+}")
    public String deleteImage(@PathVariable String filename, Model model, RedirectAttributes redirectAttributes) {
        try {
            boolean existed = storageService.delete(filename);

            if (existed) {
                redirectAttributes.addFlashAttribute(STR_MESSAGE, "Delete the image successfully: " + filename);
            } else {
                redirectAttributes.addFlashAttribute(STR_MESSAGE, "The image does not exist!");
            }
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute(STR_MESSAGE,
                    "Could not delete the image: " + filename + ". Error: " + e.getMessage());
        }

        return "redirect:/visor/images";
    }

    @GetMapping("/visor/image/pp2")
    public String pp2(){
        return "/visor/pp2";
    }
    @GetMapping("/visor/image/pp3")
    public String pp3(){
        return "/visor/pp3";
    }
}