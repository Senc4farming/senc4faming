package com.example.senc4farming.controller;


import java.io.*;
import java.net.MalformedURLException;
import java.util.Iterator;
import java.util.Map;

import com.example.senc4farming.dto.DatosLucas2018Dto;
import com.example.senc4farming.dto.EvalScriptLaunchDto;
import com.example.senc4farming.dto.SentinelQueryFilesTiffDto;
import com.example.senc4farming.model.Dates;
import com.example.senc4farming.model.DatosLucas2018;
import com.example.senc4farming.service.*;

import jakarta.persistence.criteria.CriteriaBuilder;
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
    public String newImage() {
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
        EvalScriptLaunchDto evalScriptLaunchDto = evalScriptLaunchService.buscarDtoSinOpt(id);
        String pathcompleto =  evalScriptLaunchDto.getPathtiff();

        String nombredirinterno =  pathcompleto.substring(pathcompleto.lastIndexOf(STR_USERFILES)+10,(pathcompleto.lastIndexOf("/")));
        String uploadDir = STR_F_SRC + nombredirinterno ;
        String internalpath = uploadDir + STR_RESPONSETIFF;
        logger.info(" /visor/images Path: %s", internalpath );
        model.addAttribute(STR_IMAGE, internalpath);

        return "/visor/images";
    }
    public Number[] getMinMaxCoordsArr(JSONObject jsonObject){
        Number[] coords = new Number[4];

        try {
            JSONObject request = (JSONObject) jsonObject.get(STR_REQUESTS);
            JSONObject payload = (JSONObject) request.get(STR_PAYLOAD);
            JSONObject input   = (JSONObject) payload.get(STR_INPUT);
            JSONObject bounds  = (JSONObject) input.get(STR_BOUNDS);

            JSONArray bbox = (JSONArray) bounds.get("bbox");
            if (bbox != null && bbox.size() == 4) {
                for (int i = 0; i < 4; i++) {
                    coords[i] = (Number) bbox.get(i);
                }
            } else {
                logger.warn("BBox no válido o con tamaño distinto de 4");
            }
        } catch (Exception e) {
            logger.error("Error parseando coordenadas: {}", e.getMessage());
        }

        return coords;


    }
    private void addBoundsToModel(Model model, JSONObject json, String imagePath, String polygon, Integer idPrev) {
        Number[] coords = getMinMaxCoordsArr(json);
        logsLongLat(coords[0], coords[1], coords[2], coords[3]);
        model.addAttribute(STR_MINLONG, coords[0]);
        model.addAttribute(STR_MINLAT, coords[1]);
        model.addAttribute(STR_MAXLONG, coords[2]);
        model.addAttribute(STR_MAXLAT, coords[3]);
        model.addAttribute(STR_IMAGE, imagePath);
        model.addAttribute(STR_POLYGON, polygon);
        if (idPrev != null) model.addAttribute(STR_IDPREV, idPrev);
    }

    private void commonFunc(Integer id, Integer idPrev, Model model) {
        try {
            // Recuperamos DTO y datos necesarios
            SentinelQueryFilesTiffDto dto = service.buscarDtoSinOpt(id);
            String pathCompleto = dto.getPath();
            String polygon = dto.getSentinelQueryFilesfortiff()
                    .getFiltroListarArchivos()
                    .getPolygon();

            // Construcción de rutas internas de forma más clara
            String nombreDirInterno = pathCompleto.substring(
                    pathCompleto.lastIndexOf(STR_USERFILES), pathCompleto.lastIndexOf("/")
            );
            String uploadDir = STR_F_SRC + nombreDirInterno;
            String internalPath = uploadDir + STR_RESPONSETIFF;
            String internalPathJson = STR_API + uploadDir + STR_REQUESTJSON;

            logger.info("Path TIFF: {}", internalPath);
            logger.info("Polygon: {}", polygon);

            // Parsear JSON con coordenadas
            JSONObject jsonObject = (JSONObject) new JSONParser().parse(new FileReader(internalPathJson));

            // Añadir atributos comunes al modelo (coordenadas + imagen + polígono + idPrev)
            addBoundsToModel(model, jsonObject, internalPath, polygon, idPrev);

        } catch (IOException | ParseException e) {
            logger.error("Error procesando commonFunc: {}", e.getMessage(), e);
            model.addAttribute(STR_MESSAGE, "Error al procesar la imagen: " + e.getMessage());
        }
    }

    @GetMapping("/visor/image/{id}")
    public String getListImages(@PathVariable("id") Integer id,Model model) throws IOException,
            ParseException {
        commonFunc(id,0,model);

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
        commonFunc(id,idprev,model);

        return "/visor/imagesprevmyqueryv1";
    }
    @GetMapping("/visor/image/map/{id}/{idprev}")
    public String getListImagesMapBack(@PathVariable("id") Integer id,
                                    @PathVariable("idprev") Integer idprev,
                                    Model model) throws IOException, ParseException {
        logger.info("getListImagesMapBack");
        commonFunc(id,idprev,model);
        return "/visor/imagesprevmyqueryv1map";
    }
    @GetMapping("/visor/image/tiff/{id}/{idprev}")
    public String getListImagesTiff(@PathVariable("id") Integer id,
                                    @PathVariable("idprev") Integer idprev,
                                    Model model) throws IOException, ParseException {
        commonFunc(id,idprev,model);

        return "/visor/imagesgeotiff";
    }


    @GetMapping("/visor/image/lucaspoints")
    public String showlucaspoints(Model model, Dates dates)  {
        return STR_V_IMAGES_PREV;
    }

    @PostMapping("/visor/image/lucaspoints")
    public String showlucaspointsPost(Model model, @Valid Dates dates, BindingResult result)  {
        if (result.hasErrors()) {
            logger.error(result.getAllErrors());
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
        EvalScriptLaunchDto evalScriptLaunchDto = evalScriptLaunchService.buscarDtoSinOpt(id);
        String pathcompletotiff =  evalScriptLaunchDto.getPathtiff();
        String pathcompletojson =  evalScriptLaunchDto.getPathjson();
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
        Number minlong = getMinMaxCoordsArr(jsonObject)[0];
        Number minlat = getMinMaxCoordsArr(jsonObject)[1];
        Number maxlong = getMinMaxCoordsArr(jsonObject)[2];
        Number maxlat = getMinMaxCoordsArr(jsonObject)[3];

        logsLongLat( minlong,  minlat,  maxlong,  maxlat  );

        //Buscar bounds
        //Enviar min lond, min lat , maz long max lat
        // usar dichos valores para mostrar el poígono
        addBoundsToModel(model,jsonObject,internaltiffautopath,evalScriptLaunchDto.getPolygon(),null);
        model.addAttribute(STR_MINLONG, minlong);
        model.addAttribute(STR_MINLAT, minlat);
        model.addAttribute(STR_MAXLONG, maxlong);
        model.addAttribute(STR_MAXLAT, maxlat);
        model.addAttribute(STR_IMAGE, internaltiffautopath);
        model.addAttribute(STR_POLYGON, evalScriptLaunchDto.getPolygon());

        return "/visor/imagesprevmyqueryv1";
    }

    @GetMapping("/visor/image/lucas/{id}")
    public String getPathImags(@PathVariable("id") Long id,Model model) throws IOException, ParseException {
        DatosLucas2018Dto datosLucas2018Dto = datosLucas2018Service.buscarDtoSinOpt(id);
        String pathcompleto =  datosLucas2018Dto.getPath();
        //Traducimos a  la imagen en local
        logger.info("Path inicial: %s" , pathcompleto);


        String internaltifffloat32path = pathcompleto.replace(STR_APP,STR_API );
        String internaljsonfloat32path = internaltifffloat32path.replace("response.tiff","request.json" );
        //Buscanmos el path para la imagen a mostrar
        //Obtenemos el id del punto y la banda
        DatosLucas2018 datosLucas2018 = datosLucas2018Service.buscarSinOpt(id);
        // Con los datos buscamos los registros con auto el json y el tiff
        //Buscamos el tiff
        DatosLucas2018 datosLucas20181TiffAuto = datosLucas2018Service.getlucasreglike(
                datosLucas2018.getSearchid(),
                datosLucas2018.getPointid(),
                datosLucas2018.getBand(), "%AUTO%response.tiff");
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
        Number minlong = getMinMaxCoordsArr(jsonObject)[0];
        Number minlat = getMinMaxCoordsArr(jsonObject)[1];
        Number maxlong = getMinMaxCoordsArr(jsonObject)[2];
        Number maxlat = getMinMaxCoordsArr(jsonObject)[3];

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