package com.example.sen4farming.web.controller;

import com.example.sen4farming.apiitem.Listfilestiff;
import com.example.sen4farming.config.ConfiguationProperties;
import com.example.sen4farming.config.details.SuperCustomerUserDetails;
import com.example.sen4farming.dto.*;

import com.example.sen4farming.model.SentinelQueryFiles;
import com.example.sen4farming.service.*;
import com.example.sen4farming.util.CsvGeneratorUtil;

import jakarta.servlet.http.HttpSession;

import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.*;


import java.util.*;


@Controller
public class AppCallApiSenc4farmingAsync extends AbstractController <GrupoTrabajoDto> {
    @Autowired
    private CsvGeneratorUtil csvGeneratorUtil;

    private final GrupoService service;
    private final SentinelQueryFilesService sentinelQueryFilesService;
    private final FiltroConsultaKalmanService filtroConsultaKalmanService;
    private final SentinelQueryFilesTiffService sentinelQueryFilesTiffService;

    private List<Listfilestiff> objlistfilestiff;



    private final UploadedFilesService uploadedFilesService;

    private final ConfiguationProperties configuationProperties;
    private static final HttpClient AsymcHttpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    public AppCallApiSenc4farmingAsync(MenuService menuService, GrupoService service,
                                       FiltroListarArchivosService filtroListarArchivosService,
                                       SentinelQueryFilesService sentinelQueryFilesService,
                                       FiltroConsultaKalmanService filtroConsultaKalmanService, SentinelQueryFilesTiffService sentinelQueryFilesTiffService,
                                       EvalScriptService evalScriptService, EvalScriptLaunchService evalScriptLaunchService,
                                       List<Listfilestiff> objlistfilestiff,
                                       UsuarioService usuarioService,
                                       UploadedFilesService uploadedFilesService, ConfiguationProperties configuationProperties) {
        super(menuService);
        this.service = service;
        this.sentinelQueryFilesService = sentinelQueryFilesService;
        this.filtroConsultaKalmanService = filtroConsultaKalmanService;
        this.sentinelQueryFilesTiffService = sentinelQueryFilesTiffService;
        this.objlistfilestiff = objlistfilestiff;
        this.uploadedFilesService = uploadedFilesService;
        this.configuationProperties = configuationProperties;
    }
    /**
     * Example for sending an asynchronous POST request
     *
     * @throws InterruptedException
     * @throws java.util.concurrent.ExecutionException
     */
    private static void demo3() throws ExecutionException, InterruptedException {

        System.out.println("Demo 3");

        var postRequest = HttpRequest.newBuilder()
                .uri(URI.create("https://postman-echo.com/post"))
                .header("Content-Type", "text/plain")
                .POST(HttpRequest.BodyPublishers.ofString("Hi there!"))
                .build();

        ExecutorService executor = Executors.newSingleThreadExecutor();
        var client = HttpClient.newBuilder().executor(executor).build();

        var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());

        responseFuture.thenApply(res -> {
                    System.out.printf("StatusCode: %s%n", res.statusCode());
                    return res;
                })
                .thenApply(HttpResponse::body)
                .thenAccept(System.out::println)
                .get();

        executor.shutdownNow();
    }
    @GetMapping ("/api/uploadedfiles/getreflecance/gee/{opt}/{id}")
    public String getreplectancegeecsv (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url

        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance gee: elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/gee/proc/download/csv/";
            //Obtenemos los datos del usuario de la sesión
            String userName = "no informado";
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());

            //Convert csv file to json
            String csvFile = optuploadedFilesDto.get().getPath() + "/" + optuploadedFilesDto.get().getDescription();
            //Como encontré datos, hago la llamada asincrona

            System.out.println("getreflecance gee: paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("dirstr", 1);
                requestParam.put("cloudcover", 10);
                requestParam.put("offset", 0.01);
                requestParam.put("numberOfGeeImages", 40);
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put("satellite", "landsat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = optuploadedFilesDto.get().getPath() + "/" + optuploadedFilesDto.get().getDescription();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance gee: paso 2");


                //Se invoca a la URL
                System.out.println("gee Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }

    @GetMapping ("/api/uploadedfiles/getreflecance/copsh/{opt}/{id}")
    public String getreplectancecopshcsv (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,
                                          Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance copsh: elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/copsh/proc/download/csv/";
            //Obtenemos los datos del usuario de la sesión
            String userName = "no informado";
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());

            //Convert csv file to json
            String csvFile = optuploadedFilesDto.get().getPath() + "/" + optuploadedFilesDto.get().getDescription();
            //Como encontré datos, hago la llamada asincrona

            System.out.println("getreflecance copsh : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("offset", 0.01);
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("dirstr", 1);
                requestParam.put("cloudcover", 10);
                requestParam.put("sentsecret", "ubu");
                requestParam.put("mosaickingorder", "--");
                requestParam.put("mode","s2l2a");
                requestParam.put("numdias",15);
                requestParam.put("prec","all");
                if (opt == 1){
                    requestParam.put("satellite", "landsat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = optuploadedFilesDto.get().getPath() + "/" + optuploadedFilesDto.get().getDescription();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance  copsh: paso 2");


                //Se invoca a la URL
                System.out.println("copsh Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                System.out.println(responseFuture);
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }


    @GetMapping ("/api/uploadedfiles/runknn/copsh/{opt}/{id}")
    public String runknncsvcopsh (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/knn/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());

            System.out.println("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put("satellite", "landstat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance : paso 2");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }

    @GetMapping ("/api/uploadedfiles/runknn/gee/{opt}/{id}")
    public String runknncsvgee (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/knn/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());

            System.out.println("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put("satellite", "landstat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance : paso 2");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }

    @GetMapping ("/api/uploadedfiles/runsvr/copsh/{opt}/{id}")
    public String runsvrcsvcopsh (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/svr/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());


            System.out.println("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put("satellite", "landstat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance : paso 2");


                //Se invoca a la URL
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            } finally {
                interfazConPantalla.addAttribute("resultado", "");
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }

    @GetMapping ("/api/uploadedfiles/runsvr/gee/{opt}/{id}")
    public String runsvrcsvgee (@PathVariable("id") Integer id,@PathVariable("opt") Integer opt,Model interfazConPantalla,HttpSession session) throws Exception {
        //componemos la url
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        System.out.println("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()){
            System.out.println("getreflecance : elemento encontrado");
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/csv/svr/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());


            System.out.println("getreflecance : paso 1");
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("user_id", superCustomerUserDetails.getUserID());
                requestParam.put("reference", optuploadedFilesDto.get().getId());
                if (opt == 1){
                    requestParam.put("satellite", "landstat");
                }else if (opt == 2)
                {
                    requestParam.put("satellite", "sentinel");
                }
                String pathcompleto = new StringBuilder().append(optuploadedFilesDto.get().getPath()).append("/").append(optuploadedFilesDto.get().getDescription()).toString();
                requestParam.put("path", pathcompleto);
                System.out.println("getreflecance : paso 2");


                //Se invoca a la URL
                System.out.println("Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                var postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();

                ExecutorService executor = Executors.newSingleThreadExecutor();
                var client = HttpClient.newBuilder().executor(executor).build();

                var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
                interfazConPantalla.addAttribute("resultado", "Process launched, view csv reflectance in 15 minutes");
                return "upload/processlaunched";
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "upload/processlaunched";
            }
        } else {
            interfazConPantalla.addAttribute("resultado", "csv file not found");
            return "upload/processlaunched";
        }
    }


    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/downloadbands/async/{idquery}")
    public String listfilesDownloadbands(@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) throws Exception {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = sentinelQueryFilesService.getRepo().findById(id);
        if (sentinelQueryFiles.isPresent()) {
            SentinelQueryFiles sentinelQueryFiles1 = sentinelQueryFiles.get();
            //componemos la url
            String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/sentinel/decargartiffbandas/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            System.out.println(superCustomerUserDetails.getUsername());

            //Instancia en memoria del dto a informar en la pantalla
            Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
            //Check if credentials exists
            String sessionKeycliid = "clienteid";
            String sessionKeySecret = "secret";
            String sessionAccess_token = "access_token";
            Object cliId = session.getAttribute(sessionKeycliid);
            Object secret = session.getAttribute(sessionKeySecret);
            Object token = session.getAttribute(sessionAccess_token);
            System.out.println("Encontré el token en la sesión");
            System.out.println((String) token);
            if (cliId != null) {
                copernicuscredentials.setClientid((String) cliId);
                copernicuscredentials.setSecret((String) secret);
                copernicuscredentials.setToken((String) token);


                //Obtenemos el id del usuario y el grupo
                FiltroListarArchivosDto filtroListarArchivosdto = null;
                try {
                    JSONObject requestParam = new JSONObject();
                    requestParam.put("userid", superCustomerUserDetails.getUserID());
                    requestParam.put("queryid", sentinelQueryFiles.get().getId());
                    requestParam.put("offset", 0.1);
                    requestParam.put("reference", sentinelQueryFiles.get().getFiltroListarArchivos().getReference());
                    requestParam.put("date", sentinelQueryFiles.get().getPublicationDate());
                    requestParam.put("polygon", sentinelQueryFiles.get().getFiltroListarArchivos().getPolygon());
                    requestParam.put("geofootprint", sentinelQueryFiles.get().getGeofootprint());
                    requestParam.put("cloudcover", sentinelQueryFiles.get().getFiltroListarArchivos().getCloudCover());
                    requestParam.put("sentinelfilename", sentinelQueryFiles.get().getName());
                    requestParam.put("sentinelfileid", sentinelQueryFiles.get().getSentinelId());
                    requestParam.put("clienteid", copernicuscredentials.getClientid());
                    requestParam.put("secret", copernicuscredentials.getSecret());
                    requestParam.put("token",  token);
                    //Comprobamos el patron
                    //Se invoca a la URL asincronamente
                    System.out.println("Post pantalla de busqueda 50");
                    //Lanzamos la peticioon asincrona
                    byte[] request = requestParam.toString().getBytes();

                    var postRequest = HttpRequest.newBuilder()
                            .uri(URI.create(urltext))
                            .version(HttpClient.Version.HTTP_2)
                            .header("Content-Type", "application/json")
                            .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                            .build();

                    ExecutorService executor = Executors.newSingleThreadExecutor();
                    var client = HttpClient.newBuilder().executor(executor).build();

                    var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());

                    interfazConPantalla.addAttribute("resultado", "Process launched, list files in 15 minutes");
                    return "sentinelqueryfiles/processlaunched";
                } catch (Exception e) {
                    System.out.println("Error Message");
                    System.out.println(e.getClass().getSimpleName());
                    System.out.println(e.getMessage());
                    interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                    return "sentinelqueryfiles/processlaunched";
                }
            } else {
                interfazConPantalla.addAttribute("consulta", copernicuscredentials);
                return "redirect:/api/credentials";
            }
        }
        else{
            return "redirect:/api/credentials";
        }

    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/downloadbands/async/wait/{idquery}")
    public String listfilesDownloadbandswait(@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) throws Exception {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = sentinelQueryFilesService.getRepo().findById(id);
        SentinelQueryFiles sentinelQueryFiles1 = new SentinelQueryFiles();
        if (sentinelQueryFiles.isPresent()) {
            sentinelQueryFiles1 = sentinelQueryFiles.get();
        }
        //componemos la url
        String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/sentinel/decargartiffbandas/";
        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        System.out.println(superCustomerUserDetails.getUsername());

        //Instancia en memoria del dto a informar en la pantalla
        Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
        //Check if credentials exists
        String sessionKeycliid = "clienteid";
        String sessionKeySecret = "secret";
        String sessionAccess_token = "access_token";
        Object cliId = session.getAttribute(sessionKeycliid);
        Object secret = session.getAttribute(sessionKeySecret);
        Object token = session.getAttribute(sessionAccess_token);
        System.out.println("Encontré el token en la sesión");
        System.out.println((String) token);
        if (cliId != null) {
            copernicuscredentials.setClientid((String) cliId);
            copernicuscredentials.setSecret((String) secret);
            copernicuscredentials.setToken((String) token);


            //Obtenemos el id del usuario y el grupo
            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put("userid", superCustomerUserDetails.getUserID());
                requestParam.put("queryid", sentinelQueryFiles.get().getId());
                requestParam.put("offset", 0.1);
                requestParam.put("reference", sentinelQueryFiles.get().getFiltroListarArchivos().getReference());
                requestParam.put("date", sentinelQueryFiles.get().getPublicationDate());
                requestParam.put("polygon", sentinelQueryFiles.get().getFiltroListarArchivos().getPolygon());
                requestParam.put("geofootprint", sentinelQueryFiles.get().getGeofootprint());
                requestParam.put("cloudcover", sentinelQueryFiles.get().getFiltroListarArchivos().getCloudCover());
                requestParam.put("sentinelfilename", sentinelQueryFiles.get().getName());
                requestParam.put("sentinelfileid", sentinelQueryFiles.get().getSentinelId());
                requestParam.put("clienteid", copernicuscredentials.getClientid());
                requestParam.put("secret", copernicuscredentials.getSecret());
                requestParam.put("token",  token);
                //Comprobamos el patron
                //Se invoca a la URL asincronamente
                System.out.println("Post pantalla de busqueda 50");
                //Lanzamos la peticioon asincrona
                byte[] request = requestParam.toString().getBytes();

                HttpRequest postRequest = HttpRequest.newBuilder()
                        .uri(URI.create(urltext))
                        .version(HttpClient.Version.HTTP_2)
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                        .build();
                CompletableFuture<HttpResponse<String>> AsyncResponse = null;

                // sendAsync(): Sends the given request asynchronously using this client with the given response body handler.
                //Equivalent to: sendAsync(request, responseBodyHandler, null).
                AsyncResponse = AsymcHttpClient.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());

                String strAsyncResultBody = null;
                int intAsyncResultStatusCode = 0;

                try {
                    strAsyncResultBody = AsyncResponse.thenApply(HttpResponse::body).get(5, TimeUnit.SECONDS);

                    // OR:

                    // join(): Returns the result value when complete, or throws an (unchecked) exception if completed exceptionally.
                    // To better conform with the use of common functional forms,
                    // if a computation involved in the completion of this CompletableFuture threw an exception,
                    // this method throws an (unchecked) CompletionException with the underlying exception as its cause.

                    HttpResponse<String> response = AsyncResponse.join();
                    intAsyncResultStatusCode = AsyncResponse.thenApply(HttpResponse::statusCode).get(5, TimeUnit.SECONDS);
                } catch (InterruptedException | ExecutionException | TimeoutException e) {
                    e.printStackTrace();
                }
                System.out.println("=============== AsyncHTTPClient Body:===============  \n" + strAsyncResultBody);
                System.out.println("\n=============== AsyncHTTPClient Status Code:===============  \n" + intAsyncResultStatusCode);


                String jsonArray = strAsyncResultBody;
                try {
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
                                System.out.println("valores para el json");
                                System.out.println("Key:" + key + ":: keyint:" + keyint + "::  value:" +
                                        jsonObject1.get(keyint).toString());
                                Listfilestiff itemlistfilesCheck = findfiletiffrecord(keyint);
                                System.out.println("qqqqqqqq");
                                if (itemlistfilesCheck.getKey().equals(-1)) {
                                    System.out.println("valores para el json no existe indice");
                                    Listfilestiff itmlistfilesnew = new Listfilestiff();
                                    setlistfilestifffield(key, jsonObject1, keyint, itmlistfilesnew, 0);
                                } else {
                                    // You use this ".get()" method to actually get your Listfiles from the Optional object
                                    System.out.println(" /api/listfiles/downloadbands get valores para el json existe indice");

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
                } catch (JSONException err) {
                    System.out.println("Error: " + err.toString());
                }
                //Eliminamos los resultados de la consulta anterior por referencia
                System.out.println("sentinelQueryFilesTiffService borramos para el id de files");
                System.out.println(sentinelQueryFiles1.getId());
                sentinelQueryFilesTiffService.getRepo().deleteSentinelQueryFilesTiffBySentinelQueryFilesfortiff_Id(sentinelQueryFiles1.getId());

                if (!objlistfilestiff.isEmpty()) {
                    //Guardamos los datos
                    sentinelQueryFilesService.getRepo().save(sentinelQueryFiles1);


                    //Guardamos desde la lista
                    sentinelQueryFilesTiffService.guardarDesdeConsulta(objlistfilestiff, sentinelQueryFiles1.getId());

                    return String.format("redirect:/sentinelqueryfiles/filter/" + sentinelQueryFiles.get().getId());

                } else {
                    //Mostrar página usuario no existe
                    return "sentinelqueryfiles/detallesnoencontrado";
                }
            } catch (Exception e) {
                System.out.println("Error Message");
                System.out.println(e.getClass().getSimpleName());
                System.out.println(e.getMessage());
                interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
                return "redirect:/sentinelqueryfiles";
            }
        } else {
            interfazConPantalla.addAttribute("consulta", copernicuscredentials);
            return "redirect:/api/credentials";
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
            case "path":
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


        System.out.println("getkalman : elemento encontrado");
        Optional<FiltroConsultaKalmanDto> filtroConsultaKalmanDtoOpt = filtroConsultaKalmanService.encuentraPorId(idfilter);
        if (filtroConsultaKalmanDtoOpt.isPresent()){
            FiltroConsultaKalmanDto filtroConsultaKalmanDto = filtroConsultaKalmanDtoOpt.get();
            if (optsat == 1){
                filtroConsultaKalmanDto.setSatellite("landsat");
            }else if (optsat == 2)
            {
                filtroConsultaKalmanDto.setSatellite("sentinel");
            }
            if (optkalman == 1){
                filtroConsultaKalmanDto.setKalmanpred("soc");
            }else if (optkalman == 2)
            {
                filtroConsultaKalmanDto.setKalmanpred("reflectance");
            }
            filtroConsultaKalmanDto.setPointid(pointid);
            filtroConsultaKalmanDto.setReference(String.valueOf(idfilter));
            FiltroConsultaKalmanDto dto = filtroConsultaKalmanService.guardar(filtroConsultaKalmanDto);
            //Mostramos la pantalla de ejecucion

            System.out.println("getkalman gee: paso 1");
            interfazConPantalla.addAttribute("filtro", dto);
            return "kalman/consultakalman";
        }
        else{
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
        }


    }
    @PostMapping ("/api/uploadedfiles/kalman/gee/{optkalman}/{optsat}/{idfilter}/{id}")
    public String postkalman (@PathVariable("id") Integer pointid,
                             @PathVariable("optsat") Integer optsat,
                              @PathVariable("idfilter") Integer idfilter,
                             @PathVariable("optkalman") Integer optkalman,
                              @ModelAttribute(name ="filtro") FiltroConsultaKalmanDto filtroConsultaKalmanDto,
                             Model interfazConPantalla,HttpSession session) throws Exception {
        System.out.println("postkalman : elemento encontrado");
        System.out.println("filtroConsultaKalmanDto.getNumDaysSerie()");
        System.out.println(filtroConsultaKalmanDto.getId());
        FiltroConsultaKalmanDto dtofiltroConsultaKanlamDto = filtroConsultaKalmanService.guardar(filtroConsultaKalmanDto);
        String urltext = "http://" + configuationProperties.getIppythonserver() + ":8100/api/gee/proc/download/kalman/point/";

        //Hago la llamada asincrona

        System.out.println("postkalman gee: paso 1");
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
            requestParam.put("offset", dtofiltroConsultaKanlamDto.getOffset());
            requestParam.put("cloudcover", dtofiltroConsultaKanlamDto.getCloudCover());
            requestParam.put("numberOfGeeImages", dtofiltroConsultaKanlamDto.getNumberOfGeeImages());
            requestParam.put("reference", dtofiltroConsultaKanlamDto.getReference());
            requestParam.put("user_id", dtofiltroConsultaKanlamDto.getUserid());
            requestParam.put("num_days_serie", dtofiltroConsultaKanlamDto.getNumDaysSerie());
            requestParam.put("satellite", dtofiltroConsultaKanlamDto.getSatellite());
            requestParam.put("kalmanpred", dtofiltroConsultaKanlamDto.getKalmanpred());
            requestParam.put("dirstr", dtofiltroConsultaKanlamDto.getDirstr());
            requestParam.put("origin", dtofiltroConsultaKanlamDto.getOrigin());
            requestParam.put("path", dtofiltroConsultaKanlamDto.getPath());

            System.out.println("postkalman gee: paso 2");


            //Se invoca a la URL
            System.out.println("postkalman Post pantalla de busqueda 50");
            //Lanzamos la peticioon asincrona
            byte[] request = requestParam.toString().getBytes();

            var postRequest = HttpRequest.newBuilder()
                    .uri(URI.create(urltext))
                    .version(HttpClient.Version.HTTP_2)
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofByteArray(request))
                    .build();

            ExecutorService executor = Executors.newSingleThreadExecutor();
            var client = HttpClient.newBuilder().executor(executor).build();

            var responseFuture = client.sendAsync(postRequest, HttpResponse.BodyHandlers.ofString());
            interfazConPantalla.addAttribute("resultado", "Process launched, view results in 15 minutes");
            interfazConPantalla.addAttribute("csvid", dtofiltroConsultaKanlamDto.getCsvid());
            return "upload/processlaunchedkalman";
        } catch (Exception e) {
            System.out.println("Error Message");
            System.out.println(e.getClass().getSimpleName());
            System.out.println(e.getMessage());
            interfazConPantalla.addAttribute("resultado", "Error Message :" + e.getClass().getSimpleName() + e.getMessage());
            interfazConPantalla.addAttribute("csvid", dtofiltroConsultaKanlamDto.getCsvid());
            return "upload/processlaunchedkalman";
        }
    }
}
