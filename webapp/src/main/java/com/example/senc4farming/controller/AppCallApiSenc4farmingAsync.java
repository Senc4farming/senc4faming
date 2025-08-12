package com.example.senc4farming.controller;

import com.example.senc4farming.apiitem.Listfilestiff;
import com.example.senc4farming.config.ConfiguationProperties;
import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.*;

import com.example.senc4farming.model.SentinelQueryFiles;
import com.example.senc4farming.service.*;

import jakarta.servlet.http.HttpSession;

import org.json.JSONObject;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

import java.io.File;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.*;


import java.util.*;


@Controller
public class AppCallApiSenc4farmingAsync extends AbstractController <GrupoTrabajoDto> {



    private final GrupoService service;
    private final SentinelQueryFilesService sentinelQueryFilesService;
    private final FiltroConsultaKalmanService filtroConsultaKalmanService;
    private final SentinelQueryFilesTiffService sentinelQueryFilesTiffService;

    private List<Listfilestiff> objlistfilestiff;



    private final UploadedFilesService uploadedFilesService;

    private final ConfiguationProperties configuationProperties;
    private static final String STR_QUERYID="queryid";
    private static final String STR_USERID="userid";
    private static final String STR_USER_ID="user_id";
    private static final String STR_OFFSET="offset";
    private static final String STR_REFERENCE="reference";
    private static final String STR_DATE="date";
    private static final String STR_POLYGON="polygon";
    private static final String STR_GEOFOOTPRINT="geofootprint";
    private static final String STR_CLOUDCOVER="cloudcover";
    private static final String STR_SENTINELFILENAME="sentinelfilename";
    private static final String STR_SENTINELFILEID="sentinelfileid";
    private static final String STRCLIENTID="clienteid";
    private static final String STRSECRET="secret";
    private static final String STRTOKEN="token";
    private static final String STR_RESULTADO = "resultado";
    private static final String STR_ERRORMSG="Error Message :";
    private static final String STR_REDIRECT_SENTINELQUERYFILES = "redirect:/sentinelqueryfiles";
    private static final String STR_PATH="path";
    private static final String STR_REFLECTANCE="reflectance";
    private static final String STR_CONSULTA="consulta";
    private static final String STR_UPLOAD_DETALLES_NO_ENCONTRADO="upload/detallesnoencontrado";
    private static final String STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO = "sentinelqueryfiles/detallesnoencontrado";
    private static final String STR_REDIRECT_API_CREDENTIALS =  "redirect:/api/credentials";
    private static final String STR_SATELLITE ="satellite";
    private static final String STR_HTTP = "http://";
    private static final String STR_CSV_FILE_NOT_FOUND = "csv file not found";
    private static final String STR_GET_REFL_ENCONTRADO ="getreflecance : elemento encontrado";

    private static final String STR_UPLOAD_PROC_LAUNCHED= "upload/processlaunched";

    private static final String STR_LANDSAT = "landsat";
    private static final String STR_SENTINEL = "sentinel";
    private static final String STR_PROC_LAUNCHED ="Process launched, view csv reflectance in 15 minutes";

    private static final String STR_DISTR ="dirstr";
    private static final String STR_CONTENT_TYPE ="Content-Type";
    private static final String STR_APPLICATION_JSON ="application/json";
    private static final HttpClient AsymcHttpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    public AppCallApiSenc4farmingAsync(MenuService menuService,  GrupoService service,
                                       SentinelQueryFilesService sentinelQueryFilesService,
                                       FiltroConsultaKalmanService filtroConsultaKalmanService,
                                       SentinelQueryFilesTiffService sentinelQueryFilesTiffService,
                                       List<Listfilestiff> objlistfilestiff,
                                       UploadedFilesService uploadedFilesService,
                                       ConfiguationProperties configuationProperties) {
        super(menuService);
        this.service = service;
        this.sentinelQueryFilesService = sentinelQueryFilesService;
        this.filtroConsultaKalmanService = filtroConsultaKalmanService;
        this.sentinelQueryFilesTiffService = sentinelQueryFilesTiffService;
        this.objlistfilestiff = objlistfilestiff;
        this.uploadedFilesService = uploadedFilesService;
        this.configuationProperties = configuationProperties;
    }

    @GetMapping ("/api/uploadedfiles/getreflecance/gee/{opt}/{id}")
    public String getreplectancegeecsv (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) {
        //componemos la url

        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance gee: elemento leido");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/gee/proc/download/csv/";
            //Obtenemos los datos del usuario de la sesión

            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());

            //Como encontré datos, hago la llamada asincrona

            logger.info("getreflecance gee: paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_DISTR, 1);
                requestParam.put(STR_CLOUDCOVER, 10);
                requestParam.put(STR_OFFSET, 0.01);
                requestParam.put("numberOfGeeImages", 40);
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                File  itm = new File(optuploadedFilesDto.get().getPath(),optuploadedFilesDto.get().getDescription());
                requestParam.put(STR_PATH, itm.getPath());
                logger.info("getreflecance gee: paso 2");


                //Se invoca a la URL
                logger.info("gee Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info("============  client.sendAsync :===============  %s " , responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);
        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }

    @GetMapping ("/api/uploadedfiles/getreflecance/copsh/{opt}/{id}")
    public String getreplectancecopshcsv (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,
                                          Model interfazConPantalla,HttpSession session) {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance copsh: elemento leido");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/copsh/proc/download/csv/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());

            //Como encontré datos, hago la llamada asincrona

            logger.info("getreflecance copsh : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_OFFSET, 0.01);
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_DISTR, 1);
                requestParam.put(STR_CLOUDCOVER, 10);
                requestParam.put("sentsecret", "ubu");
                requestParam.put("mosaickingorder", "--");
                requestParam.put("mode","s2l2a");
                requestParam.put("numdias",15);
                requestParam.put("prec","all");
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                File  itm = new File(optuploadedFilesDto.get().getPath(),optuploadedFilesDto.get().getDescription());
                requestParam.put(STR_PATH, itm.getPath());
                logger.info("getreflecance  copsh: paso 2");


                //Se invoca a la URL
                logger.info("copsh Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info(responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);

            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);

        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }


    @GetMapping ("/api/uploadedfiles/runknn/copsh/{opt}/{id}")
    public String runknncsvcopsh (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance : elemento leido ");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/knn/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());

            logger.info("getreflecance : paso 1 ");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USER_ID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put(STR_PATH, pathcompleto);
                logger.info("getreflecance: paso 2");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info("===========  client.sendAsync :===============  %s " , responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);
        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }

    @GetMapping ("/api/uploadedfiles/runknn/gee/{opt}/{id}")
    public String runknncsvgee (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session)  {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance: elemento leido");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/knn/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());

            logger.info("getreflecance: paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USER_ID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put(STR_PATH, pathcompleto);
                logger.info("getreflecance : paso 2 ");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info("==========  client.sendAsync :===============  %s " , responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);
        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }

    @GetMapping ("/api/uploadedfiles/runsvr/copsh/{opt}/{id}")
    public String runsvrcsvcopsh (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session)  {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/svr/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());


            logger.info("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USER_ID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put(STR_PATH, pathcompleto);
                logger.info("getreflecance : paso 2");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info("===============  client.sendAsync :============  %s " , responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());

            } finally {
                interfazConPantalla.addAttribute(STR_RESULTADO, "");
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);
        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }

    @GetMapping ("/api/uploadedfiles/runsvr/gee/{opt}/{id}")
    public String runsvrcsvgee (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            logger.info(STR_GET_REFL_ENCONTRADO);
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/svr/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());


            logger.info("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USER_ID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_REFERENCE, optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, STR_LANDSAT);
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, STR_SENTINEL);
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put(STR_PATH, pathcompleto);
                logger.info("getreflecance : paso 2");


                //Se invoca a la URL
                logger.info("Post pantalla de busqueda 50 ");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                logger.info("============  client.sendAsync :============  %s " , responseFuture);
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_PROC_LAUNCHED);
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            }
        } else {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_CSV_FILE_NOT_FOUND);
        }
        return STR_UPLOAD_PROC_LAUNCHED;
    }


    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/downloadbands/async/{idquery}")
    public String listfilesDownloadbands(@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = sentinelQueryFilesService.getRepo().findById(id);
        if (sentinelQueryFiles.isPresent()) {
            //componemos la url
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/sentinel/decargartiffbandas/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());

            //Instancia en memoria del dto a informar en la pantalla
            Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
            //Check if credentials exists
            Object cliId = session.getAttribute(STRCLIENTID);
            Object secret = session.getAttribute(STRSECRET);
            Object token = session.getAttribute(STRTOKEN);
            logger.info("Encontré el token en la sesión");
            logger.info((String) token);
            if (cliId != null) {
                copernicuscredentials.setClientid((String) cliId);
                copernicuscredentials.setSecret((String) secret);
                copernicuscredentials.setToken((String) token);


                //Obtenemos el id del usuario y el grupo
                try {
                    JSONObject requestParam = new JSONObject();
                    requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                    requestParam.put(STR_QUERYID, sentinelQueryFiles.get().getId());
                    requestParam.put(STR_OFFSET, 0.1);
                    requestParam.put(STR_REFERENCE, sentinelQueryFiles.get().getFiltroListarArchivos().getReference());
                    requestParam.put(STR_DATE, sentinelQueryFiles.get().getPublicationDate());
                    requestParam.put(STR_POLYGON, sentinelQueryFiles.get().getFiltroListarArchivos().getPolygon());
                    requestParam.put(STR_GEOFOOTPRINT, sentinelQueryFiles.get().getGeofootprint());
                    requestParam.put(STR_CLOUDCOVER, sentinelQueryFiles.get().getFiltroListarArchivos().getCloudCover());
                    requestParam.put(STR_SENTINELFILENAME, sentinelQueryFiles.get().getName());
                    requestParam.put(STR_SENTINELFILEID, sentinelQueryFiles.get().getSentinelId());
                    requestParam.put(STRCLIENTID, copernicuscredentials.getClientid());
                    requestParam.put(STRSECRET, copernicuscredentials.getSecret());
                    requestParam.put(STRTOKEN,  token);
                    //Comprobamos el patron
                    //Se invoca a la URL asincronamente
                    logger.info("Post pantalla de busqueda 50");
                    //Lanzamos la peticioon asincrona
                    byte[] request = requestParam.toString().getBytes();

                    var postRequest = HttpRequest.newBuilder()
                            .uri(URI.create(urltext))
                            .version(HttpClient.Version.HTTP_2)
                            .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                            .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                            .build();

                    ExecutorService executor = Executors.newSingleThreadExecutor();
                    var client = HttpClient.newBuilder().executor(executor).build();

                    var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                    logger.info("===============  client.sendAsync :===============  %s " , responseFuture);
                    interfazConPantalla.addAttribute(STR_RESULTADO, "Process launched, list files in 15 minutes");
                    return "sentinelqueryfiles/processlaunched";
                } catch (Exception e) {
                    logger.info(STR_ERRORMSG);
                    logger.info(e.getClass().getSimpleName());
                    logger.info(e.getMessage());
                    interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                    return "sentinelqueryfiles/processlaunched";
                }
            } else {
                interfazConPantalla.addAttribute(STR_CONSULTA, copernicuscredentials);
                return STR_REDIRECT_API_CREDENTIALS;
            }
        }
        else{
            return STR_REDIRECT_API_CREDENTIALS;
        }

    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/downloadbands/async/wait/{idquery}")
    public String listfilesDownloadbandswait(@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = sentinelQueryFilesService.getRepo().findById(id);
        SentinelQueryFiles sentinelQueryFiles1 = new SentinelQueryFiles();
        if (sentinelQueryFiles.isPresent()) {
            sentinelQueryFiles1 = sentinelQueryFiles.get();
        }
        //componemos la url
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/sentinel/decargartiffbandas/";
        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());

        //Instancia en memoria del dto a informar en la pantalla
        Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
        //Check if credentials exists
        Object cliId = session.getAttribute(STRCLIENTID);
        Object secret = session.getAttribute(STRSECRET);
        Object token = session.getAttribute(STRTOKEN);
        logger.info("Encontré el token en la sesión");
        logger.info((String) token);
        if (cliId != null) {
            copernicuscredentials.setClientid((String) cliId);
            copernicuscredentials.setSecret((String) secret);
            copernicuscredentials.setToken((String) token);


            //Obtenemos el id del usuario y el grupo
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                requestParam.put(STR_QUERYID, sentinelQueryFiles.get().getId());
                requestParam.put(STR_OFFSET, 0.1);
                requestParam.put(STR_REFERENCE, sentinelQueryFiles.get().getFiltroListarArchivos().getReference());
                requestParam.put(STR_DATE, sentinelQueryFiles.get().getPublicationDate());
                requestParam.put(STR_POLYGON, sentinelQueryFiles.get().getFiltroListarArchivos().getPolygon());
                requestParam.put(STR_GEOFOOTPRINT, sentinelQueryFiles.get().getGeofootprint());
                requestParam.put(STR_CLOUDCOVER, sentinelQueryFiles.get().getFiltroListarArchivos().getCloudCover());
                requestParam.put(STR_SENTINELFILENAME, sentinelQueryFiles.get().getName());
                requestParam.put(STR_SENTINELFILEID, sentinelQueryFiles.get().getSentinelId());
                requestParam.put(STRCLIENTID, copernicuscredentials.getClientid());
                requestParam.put(STRSECRET, copernicuscredentials.getSecret());
                requestParam.put(STRTOKEN,  token);
                //Comprobamos el patron
                //Se invoca a la URL asincronamente
                logger.info("Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                HttpRequest postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();
                CompletableFuture<HttpResponse<String>> asyncResponse = null;

                // sendAsync(): Sends the given request asynchronously using this client with the given response body handler.
                //Equivalent to: sendAsync(request, responseBodyHandler, null).
                asyncResponse = AsymcHttpClient.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());

                String strAsyncResultBody = null;
                int intAsyncResultStatusCode = 0;

                strAsyncResultBody = asyncResponse.thenApply(HttpResponse::body).get(5, TimeUnit.SECONDS);

                // OR:

                // join(): Returns the result value when complete, or throws an (unchecked) exception if completed exceptionally.
                // To better conform with the use of common functional forms,
                // if a computation involved in the completion of this CompletableFuture threw an exception,
                // this method throws an (unchecked) CompletionException with the underlying exception as its cause.

                HttpResponse<String> response = asyncResponse.join();
                intAsyncResultStatusCode = asyncResponse.thenApply(HttpResponse::statusCode).get(5, TimeUnit.SECONDS);
                logger.info("=============== asyncResponse :===============  %s " , response);
                logger.info("=============== AsyncHTTPClient Body:===============  %s " , strAsyncResultBody);
                logger.info("=============== AsyncHTTPClient Status Code:===============  %s " , intAsyncResultStatusCode);


                String jsonArray = strAsyncResultBody;

                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();

                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObject1 = ( jsonObject.getJSONObject(key));
                        Iterator<String> keysint = jsonObject1.keys();
                        while (keysint.hasNext()) {
                            String keyint = keysint.next();

                            Listfilestiff itemlistfilesCheck = findfiletiffrecord(keyint);

                            if (itemlistfilesCheck.getKey().equals(-1)) {
                                logger.info("valores para el json no existe indice");
                                Listfilestiff itmlistfilesnew = new Listfilestiff();
                                setlistfilestifffield(key, jsonObject1, keyint, itmlistfilesnew, 0);
                            } else {
                                // You use this ".get()" method to actually get your Listfiles from the Optional object
                                logger.info(" /api/listfiles/downloadbands get valores para el json existe indice");

                                objlistfilestiff.remove(itemlistfilesCheck);
                                setlistfilestifffield(key, jsonObject1, keyint, itemlistfilesCheck, 1);
                            }
                        }
                    }
                }
                if (objlistfilestiff.isEmpty())
                    sentinelQueryFiles1.setNunberOfTiff(0);
                else
                    sentinelQueryFiles1.setNunberOfTiff(objlistfilestiff.size());

                //Eliminamos los resultados de la consulta anterior por referencia
                logger.info("sentinelQueryFilesTiffService borramos para el id de files");
                logger.info(sentinelQueryFiles1.getId());
                sentinelQueryFilesTiffService.getRepo().deleteSentinelQueryFilesTiffBySentinelQueryFilesfortiff_Id(sentinelQueryFiles1.getId());

                if (!objlistfilestiff.isEmpty()) {
                    //Guardamos los datos
                    sentinelQueryFilesService.getRepo().save(sentinelQueryFiles1);


                    //Guardamos desde la lista
                    sentinelQueryFilesTiffService.guardarDesdeConsulta(objlistfilestiff, sentinelQueryFiles1.getId());

                    return String.format("redirect:/sentinelqueryfiles/filter/%s" , sentinelQueryFiles.get().getId());

                } else {
                    //Mostrar página usuario no existe
                    return STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO;
                }
            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                return STR_REDIRECT_SENTINELQUERYFILES;
            }
        } else {
            interfazConPantalla.addAttribute(STR_CONSULTA, copernicuscredentials);
            return STR_REDIRECT_API_CREDENTIALS;
        }
    }
    private  Listfilestiff findfiletiffrecord( String key){
        Listfilestiff listfilesini = new Listfilestiff();
        listfilesini.setKey(-1);
        for(Listfilestiff p : objlistfilestiff){
            if ( p.getKey().equals( Integer.parseInt(key)) ){
                listfilesini =  p;
            }
        }

        return listfilesini;
    }
    private void setlistfilestifffield(String key, JSONObject jsonObject1, String keyint, Listfilestiff listfilesItm
            , Integer option) {
        switch (key.toLowerCase()) {
            case "band":
                listfilesItm.setBand(jsonObject1.get(keyint).toString());
                break;
            case STR_PATH:
                listfilesItm.setPath(jsonObject1.get(keyint).toString());
                break;
            default:
                listfilesItm.setKey(Integer.valueOf(jsonObject1.get(keyint).toString()));

        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objlistfilestiff.add(listfilesItm);

        }else {
            //el elemennto no existe y se añadeç
            listfilesItm.setKey( Integer.parseInt(keyint));
            objlistfilestiff.add(listfilesItm);
        }

    }
    @GetMapping ("/api/uploadedfiles/kalman/gee/{optkalman}/{optsat}/{idfilter}/{id}")
    public String getkalman (@PathVariable("id") Integer pointid,
                                @PathVariable("optsat") Integer optsat,
                                @PathVariable("idfilter") Integer idfilter,
                                @PathVariable("optkalman") Integer optkalman,

                                Model interfazConPantalla)  {


        logger.info("getkalman : elemento encontrado");
        Optional<FiltroConsultaKalmanDto> filtroConsultaKalmanDtoOpt = filtroConsultaKalmanService.encuentraPorId(idfilter);
        if (filtroConsultaKalmanDtoOpt.isPresent()){
            FiltroConsultaKalmanDto filtroConsultaKalmanDto = filtroConsultaKalmanDtoOpt.get();
            if (optsat == 1){
                filtroConsultaKalmanDto.setSatellite(STR_LANDSAT);
            }else if (optsat == 2)
            {
                filtroConsultaKalmanDto.setSatellite(STR_SENTINEL);
            }
            if (optkalman == 1){
                filtroConsultaKalmanDto.setKalmanpred("soc");
            }else if (optkalman == 2)
            {
                filtroConsultaKalmanDto.setKalmanpred(STR_REFLECTANCE);            }
            filtroConsultaKalmanDto.setPointid(pointid);
            filtroConsultaKalmanDto.setReference(String.valueOf(idfilter));
            FiltroConsultaKalmanDto dto = filtroConsultaKalmanService.guardar(filtroConsultaKalmanDto);
            //Mostramos la pantalla de ejecucion

            logger.info("getkalman gee: paso 1");
            interfazConPantalla.addAttribute("filtro", dto);
            return "kalman/consultakalman";
        }
        else{
            //Mostrar página usuario no existe
            return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
        }


    }
    @PostMapping ("/api/uploadedfiles/kalman/gee/{optkalman}/{optsat}/{idfilter}/{id}")
    public String postkalman (@PathVariable("id") Integer pointid,
                             @PathVariable("optsat") Integer optsat,
                              @PathVariable("idfilter") Integer idfilter,
                             @PathVariable("optkalman") Integer optkalman,
                              @ModelAttribute(name ="filtro") FiltroConsultaKalmanDto filtroConsultaKalmanDto,
                             Model interfazConPantalla,HttpSession session)  {
        logger.info("postkalman : elemento encontrado");
        logger.info("filtroConsultaKalmanDto.getNumDaysSerie()");
        logger.info(filtroConsultaKalmanDto.getId());
        FiltroConsultaKalmanDto dtofiltroConsultaKanlamDto = filtroConsultaKalmanService.guardar(filtroConsultaKalmanDto);
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/gee/proc/download/kalman/point/";

        //Hago la llamada asincrona

        logger.info("postkalman gee: paso 1");
        /*
        point_id = content['pointid']
        offset = content['offset']
        num_offset = float(offset)
        cloudcover = content['cloudcover']
        num_cloud = float(cloudcover)
        numberOfGeeImages = content['numberOfGeeImages']
        reference = content['reference']
        user_id = content['user_id']
        num_days_serie_str = content['num_days_serie']
        num_days_serie = num_days_serie_str
        satellite = content['satellite']
        kalmanpred = content['kalmanpred']
        dirstr = content['dirstr']
         */
        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put("pointid", dtofiltroConsultaKanlamDto.getPointid());
            requestParam.put(STR_OFFSET, dtofiltroConsultaKanlamDto.getOffset());
            requestParam.put(STR_CLOUDCOVER, dtofiltroConsultaKanlamDto.getCloudCover());
            requestParam.put("numberOfGeeImages", dtofiltroConsultaKanlamDto.getNumberOfGeeImages());
            requestParam.put(STR_REFERENCE, dtofiltroConsultaKanlamDto.getReference());
            requestParam.put(STR_USER_ID, dtofiltroConsultaKanlamDto.getUserid());
            requestParam.put("num_days_serie", dtofiltroConsultaKanlamDto.getNumDaysSerie());
            requestParam.put(STR_SATELLITE, dtofiltroConsultaKanlamDto.getSatellite());
            requestParam.put("kalmanpred", dtofiltroConsultaKanlamDto.getKalmanpred());
            requestParam.put(STR_DISTR, dtofiltroConsultaKanlamDto.getDirstr());
            requestParam.put("origin", dtofiltroConsultaKanlamDto.getOrigin());
            requestParam.put(STR_PATH, dtofiltroConsultaKanlamDto.getPath());

            logger.info("postkalman gee: paso 2");


            //Se invoca a la URL
            logger.info("postkalman Post pantalla de busqueda 50");
            //Lanzamos la peticioon asincrona
            byte[] request = requestParam.toString().getBytes();

            var postRequest = HttpRequest.newBuilder()
                    .uri(URI.create(urltext))
                    .version(HttpClient.Version.HTTP_2)
                    .header(STR_CONTENT_TYPE, STR_APPLICATION_JSON)
                    .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                    .build();

            ExecutorService executor = Executors.newSingleThreadExecutor();
            var client = HttpClient.newBuilder().executor(executor).build();

            var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
            logger.info("===============  client.sendAsync :===============  %s " , responseFuture);
            interfazConPantalla.addAttribute(STR_RESULTADO, "Process launched, view results in 15 minutes");
            interfazConPantalla.addAttribute("csvid", dtofiltroConsultaKanlamDto.getCsvid());
            return "upload/processlaunchedkalman";
        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            interfazConPantalla.addAttribute("csvid", dtofiltroConsultaKanlamDto.getCsvid());
            return "upload/processlaunchedkalman";
        }
    }
}
