package com.example.jpa_formacion.web.controller;

import com.example.jpa_formacion.apiitem.*;
import com.example.jpa_formacion.config.ConfiguationProperties;
import com.example.jpa_formacion.config.details.SuperCustomerUserDetails;
import com.example.jpa_formacion.dto.*;
import com.example.jpa_formacion.model.*;
import com.example.jpa_formacion.service.*;
import com.example.jpa_formacion.util.CsvGeneratorUtil;
import com.example.jpa_formacion.util.Request;
import jakarta.servlet.http.HttpSession;
import org.json.JSONException;
import org.json.JSONObject;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;


@Controller
public class AppCallApiSenc4farming extends AbstractController <GrupoTrabajoDto> {

    private final CsvGeneratorUtil csvGeneratorUtil;

    private final CallApiSenc4farmingService callApiSenc4farmingService;

    private  List<Listfiles> objlistfiles;

    private  List<Listfilestiff> objlistfilestiff;

    private  List<ListfilesEvalScript> objlistfilesevalscript;

    private  List<DatosLucas2018Api> objlistdatoslucas2018Api;

    private  List<DatosUploadCsvApi> objlistdatosuploadcsvApi;

    private  List<UploadedFilesReflectance> objListUploadedFilesReflectances;

    private List<AIModels> objListAIModels;
    private  final UsuarioService  usuarioService;

    private final UploadedFilesService uploadedFilesService;

    private final ConfiguationProperties configuationProperties;

    private static final String  KEYLOG = "Key: {} :: keyint: {} ::  value: {} ";
    private static final String STR_ERROR = "Error : {} ";
    private static final String STR_QUERYID="queryid";
    private static final String STR_USERID="userid";
    private static final String STR_OFFSET="offset";
    private static final String STR_REFERENCE="reference";
    private static final String STR_DATE="date";
    private static final String STR_DATEFIN="datefin";
    private static final String STR_DATEINI="dateini";
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

    private static final String STR_LONGITUD="longitud";
    private static final String STR_LATITUD="latitud";
    private static final String STR_ID="id";
    private static final String STR_PATH="path";
    private static final String STR_REFLECTANCE="reflectance";
    private static final String STR_BAND="band";
    private static final String STR_SURVEY_DATE="survey_date";
    private static final String STR_OC="oc";
    private static final String STR_KEY="key";
    private static final String STR_GROUPID = "groupid";
    private static final String STR_ERRORMESSAGE ="errormessage";

    private static final String STR_CONSULTA="consulta";

    private static final String STR_SEESIONACCESSTOKEN= "access_token";

    private static final String STR_UPLOAD_DETALLES_NO_ENCONTRADO="upload/detallesnoencontrado";
    private static final String STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO = "sentinelqueryfiles/detallesnoencontrado";
    private static final String STR_AIMODELS_DETALLES_NO_ENCONTRADO ="aiodels/detallesnoencontrado";
    private static final String STR_LUCAS_DETALLES_NO_ENCONTRADO ="lucas/detallesnoencontrado";



    private static final String STR_REDIRECT_SENTINEQUERYFILESFILTER ="redirect:/sentinelqueryfiles/filter/%s";

    private static final String STR_DATOS = "datos";

    private static final String STR_REDIRECT_API_CREDENTIALS =  "redirect:/api/credentials";

    private static final String STR_LISTA = "lista";

    private static final String STR_SATELLITE ="satellite";

    private static final String STR_HTTP = "http://";
    private Random r = new Random();

    public AppCallApiSenc4farming(MenuService menuService,
                                  CsvGeneratorUtil csvGeneratorUtil, CallApiSenc4farmingService callApiSenc4farmingService, List<Listfilestiff> objlistfilestiff,
                                  UsuarioService usuarioService,
                                  UploadedFilesService uploadedFilesService, ConfiguationProperties configuationProperties) {
        super(menuService);
        this.csvGeneratorUtil = csvGeneratorUtil;
        this.callApiSenc4farmingService = callApiSenc4farmingService;
        this.objlistfilestiff = objlistfilestiff;
        this.uploadedFilesService = uploadedFilesService;
        this.configuationProperties = configuationProperties;
        this.objlistfiles = new ArrayList<>();
        this.objlistfilesevalscript = new ArrayList<>();
        this.objListUploadedFilesReflectances = new ArrayList<>();
        this.objlistdatoslucas2018Api = new ArrayList<>();
        this.objlistdatosuploadcsvApi = new ArrayList<>();
        this.objListAIModels = new ArrayList<>();
        this.usuarioService = usuarioService;
    }
    @GetMapping("/api/downloadtiff")
    public String downloadtiff(Model interfazConPantalla){
        //Listado de los EvalScript del usuario
        List<EvalScript> evalScripts = callApiSenc4farmingService.getEvalScriptService().buscarEntidades();
        //Instancia en memoria del dto a informar en la pantalla
        DownloadtiffDto downloadtiffDto = new DownloadtiffDto();
        downloadtiffDto.setFile("S2A_MSIL2A_20230901T000231_N0509_R030_T56JPT_20230901T035601.SAFE");
        downloadtiffDto.setEvalScripts(evalScripts);
        //Obtenemos los credenciales de sesión
        //Mediante "addAttribute" comparto con la pantalla
        interfazConPantalla.addAttribute(STR_DATOS,downloadtiffDto);
        logger.info("Preparando pantalla de busqueda");
        return "evalscript/descargartiff";
    }

    @GetMapping("/api/credentials")
    public String getcredentials(  Model interfazConPantalla, HttpSession session){
        //Instancia en memoria del dto a informar en la pantalla
        Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
        //Check if credentials exists
        Object cliId = session.getAttribute(STRCLIENTID);
        Object secret = session.getAttribute(STRSECRET);
        Object token =  session.getAttribute(STR_SEESIONACCESSTOKEN);
        logger.info("En GetMapping /api/credentials");
        if (cliId != null){
            logger.info("En GetMapping /api/credentials: tenemos datos en sesión");
            copernicuscredentials.setClientid((String) cliId);
            copernicuscredentials.setSecret((String) secret);
            copernicuscredentials.setToken((String) token);
        }
        logger.info("clientid");
        logger.info(copernicuscredentials.getClientid());
        //Obtenemos los credenciales de sesión
        //Mediante "addAttribute" comparto con la pantalla
        interfazConPantalla.addAttribute(STR_CONSULTA,copernicuscredentials);
        return STR_REDIRECT_API_CREDENTIALS;
    }
    @PostMapping("/api/credentials")
    public String getcredentials(@ModelAttribute(name ="consulta") Copernicuscredentials copernicuscredentials
            , HttpSession session, Model interfazConPantalla) {

        logger.info("En Postmapping /api/credentials: tenemos datos en sesión: {} " , copernicuscredentials.getClientid());
        session.setAttribute(STRCLIENTID,copernicuscredentials.getClientid() );
        session.setAttribute(STRSECRET,copernicuscredentials.getSecret());
        //llamamos a pedir el token al api

        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/sentinel/gettoken/";
        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());

        //Obtenemos el id del usuario y el grupo

        JSONObject requestParam = new JSONObject();
        requestParam.put("client_id",copernicuscredentials.getClientid());
        requestParam.put("client_secret",copernicuscredentials.getSecret());
        //Comprobamos el patron
        //Se invoca a la URL
        Request request1 = new Request(urltext, requestParam);
        //Obtenemos el token del request
        try {
            String jsonArray = request1.output;
            logger.info("Post pantalla de busqueda json leido");
            logger.info(jsonArray);

            JSONObject jsonObject = new JSONObject(jsonArray);
            if (jsonObject.has("errorcode")) {
                String text = "Credential error: " + jsonObject.get(STR_ERRORMESSAGE);
                interfazConPantalla.addAttribute(STR_ERRORMESSAGE,text);
                return STR_REDIRECT_API_CREDENTIALS;
            }
            else{
                copernicuscredentials.setToken(jsonObject.get(STRTOKEN).toString());
                session.setAttribute(STRTOKEN,jsonObject.get(STRTOKEN).toString());
                logger.info(copernicuscredentials.getToken());
                //Obtenemos los credenciales de sesión
                //Mediante "addAttribute" comparto con la pantalla
                return "index";
            }

        } catch (JSONException err) {
            logger.info(STR_ERROR, err);
            String text = "Credential error: " + err.getMessage() + ", contact administrator";
            interfazConPantalla.addAttribute(STR_ERRORMESSAGE,text);
            return STR_REDIRECT_API_CREDENTIALS;
        }



    }

    @GetMapping("/api/listfiles")
    public String listfilesGet(Model interfazConPantalla, HttpSession session){
        //Instancia en memoria del dto a informar en la pantalla
        logger.info("En /api/listfiles get");
        ListarArchivosDto listarArchivosDto = new ListarArchivosDto();
        //Instancia en memoria del dto a informar en la pantalla
        Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
        //Check if credentials exists


        Object cliId = session.getAttribute(STRCLIENTID);
        Object secret = session.getAttribute(STRSECRET);
        Object token =  session.getAttribute(STR_SEESIONACCESSTOKEN);


        if (cliId != null) {
            interfazConPantalla.addAttribute(STR_CONSULTA, listarArchivosDto);
            copernicuscredentials.setClientid((String) cliId);
            copernicuscredentials.setSecret((String) secret);
            copernicuscredentials.setToken((String) token);
            return "api/odadaconsulta";
        }
        else{
            interfazConPantalla.addAttribute(STR_CONSULTA,copernicuscredentials);
            return STR_REDIRECT_API_CREDENTIALS;
        }

    }

    @GetMapping("/api/listfiles/{id}")
    public String listfilesGetId(Model interfazConPantalla,@PathVariable(STR_ID) Integer id, HttpSession session){
        //Con el id del filtro obtenemos el filtro
        Optional<FiltroListarArchivos> listarArchivos = callApiSenc4farmingService.getFiltroListarArchivosService().buscar(id);
        if ( listarArchivos.isPresent()){
            //Instancia en memoria del dto a informar en la pantalla
            ListarArchivosDto listarArchivosDto = new ListarArchivosDto();
            listarArchivosDto.setFilterid(id);
            listarArchivosDto.setPolygon(listarArchivos.get().getPolygon());
            listarArchivosDto.setDateIni(listarArchivos.get().getDateIni());
            listarArchivosDto.setDateFin(listarArchivos.get().getDateFin());
            listarArchivosDto.setReference(listarArchivos.get().getReference());
            listarArchivosDto.setCloudCover(listarArchivos.get().getCloudCover());
            listarArchivosDto.setUserid(Long.valueOf(((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID()));
            listarArchivosDto.setUserName(((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername());
            Optional<Usuario> usuario = usuarioService.buscar(((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID());
            if (usuario.isPresent())
            {
                listarArchivosDto.setGroupid(usuario.get().getGrupoTrabajo().getId());
            }
            //Instancia en memoria del dto a informar en la pantalla
            Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
            //Check if credentials exists
            Object cliId = session.getAttribute(STRCLIENTID);
            if (cliId != null){
                interfazConPantalla.addAttribute(STR_CONSULTA,listarArchivosDto);
                return "api/odadaconsulta";
            }
            else{
                interfazConPantalla.addAttribute(STR_CONSULTA,copernicuscredentials);
                return STR_REDIRECT_API_CREDENTIALS;
            }
        }
        else {
            return "api/odadaconsultanoencontrado";
        }


    }
    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles")
    public String listfilesPost( @ModelAttribute(name ="consulta") ListarArchivosDto listarArchivosDto,
                                 Model interfazConPantalla) throws JSONException {

        logger.info("En /api/listfiles post");
        //Objeto para guardar el filtro de la consulta
        FiltroListarArchivosDto filtroListarArchivosDto = new FiltroListarArchivosDto();
        //Mensaje de error
        String strErrorMessage = "";
        //componemos la url

        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/generarlista2ANew/";

        //Obtenemos los datos del usuario de la sesión
        logger.info("Post pantalla de busqueda 21");
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());
        logger.info("Post pantalla de busqueda 22");
        //Comprobamos si hay usuario logeado
        if (superCustomerUserDetails.getUsername().equals("anonimo@anonimo")) {
            listarArchivosDto.setUserName(superCustomerUserDetails.getUsername());
            listarArchivosDto.setGroupid(0L);
            listarArchivosDto.setUserid(0L);
        } else {
            logger.info("Post pantalla de busqueda 30");

            listarArchivosDto.setUserName(superCustomerUserDetails.getUsuario().getEmail());
            listarArchivosDto.setGroupid(superCustomerUserDetails.getUsuario().getGrupoTrabajo().getId());
            listarArchivosDto.setUserid(superCustomerUserDetails.getUsuario().getId());

        }
        logger.info("Post pantalla de busqueda 40");
        //Obtenemos el id del usuario y el grupo
        FiltroListarArchivosDto filtroListarArchivosdto = null;
        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put("userName", listarArchivosDto.getUserName());
            requestParam.put(STR_GROUPID, listarArchivosDto.getGroupid());
            requestParam.put(STR_USERID, listarArchivosDto.getUserid());
            requestParam.put(STR_REFERENCE, listarArchivosDto.getReference());
            requestParam.put(STR_DATEINI, listarArchivosDto.getDateIni());
            requestParam.put(STR_DATEFIN, listarArchivosDto.getDateFin());
            requestParam.put(STR_POLYGON, listarArchivosDto.getPolygon());
            requestParam.put(STR_CLOUDCOVER, listarArchivosDto.getCloudCover());
            //Se guardan los datos para almacenar el filtro de la consulta
            filtroListarArchivosDto.setReference(listarArchivosDto.getReference());
            filtroListarArchivosDto.setPolygon(listarArchivosDto.getPolygon());
            filtroListarArchivosDto.setCloudCover(listarArchivosDto.getCloudCover());
            filtroListarArchivosDto.setDateIni(listarArchivosDto.getDateIni());
            filtroListarArchivosDto.setDateFin(listarArchivosDto.getDateFin());
            filtroListarArchivosDto.setNunberOfResults(0);
            //Con el id tengo que buscar el registro a nivel de entidad
            filtroListarArchivosDto.setUsuariofiltro(((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsuario());
            //Comprobamos el patron
            //Se invoca a la URL
            Request request1 = new Request(urltext, requestParam, 0.1F);
            logger.info(request1.output);
            logger.info(request1.errormessage);
            if (request1.errormessage.equals("")) {
                logger.info("Post pantalla de busqueda llamada realizada:{}", request1.output);
                String jsonArray = request1.output;
                logger.info("Post pantalla de busqueda json leido");
                logger.info(jsonArray);
                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();

                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                        Iterator<String> keysint = jsonObjectForKey.keys();
                        while (keysint.hasNext()) {
                            String keyint = keysint.next();
                            Listfiles itemlistfilesCheck = findfilerecord(keyint);
                            if (itemlistfilesCheck.getKey().equals(-1)) {
                                Listfiles itmlistfilesnew = new Listfiles();
                                setlistfilesfield(key, jsonObjectForKey, keyint, itmlistfilesnew, 0);
                            } else {
                                // You use this ".get()" method to actually get your Listfiles from the Optional object

                                objlistfiles.remove(itemlistfilesCheck);
                                setlistfilesfield(key, jsonObjectForKey, keyint, itemlistfilesCheck, 1);
                            }
                        }
                    }
                }
                filtroListarArchivosDto.setNunberOfResults(objlistfiles.size());

                //Eliminamos los resultados de la consulta anterior por referencia
                logger.info("Antes de eliminar datos anteriores id: {}", listarArchivosDto.getFilterid());


                logger.info("Despues de eliminar datos anteriores id: {} " , listarArchivosDto.getFilterid());

                //Guardamos los datos del filtro
                filtroListarArchivosDto.setId(listarArchivosDto.getFilterid());
                filtroListarArchivosdto = callApiSenc4farmingService.getFiltroListarArchivosService().guardar(filtroListarArchivosDto);
                logger.info("request1.getResponseHeaders()");
                logger.info(request1.getResponseHeaders());
                logger.info("request1.output");
                logger.info(request1.output);

                //Guardamos desde la lista
                callApiSenc4farmingService.getSentinelQueryFilesService().guardarDesdeConsulta(objlistfiles, filtroListarArchivosdto.getId());
                interfazConPantalla.addAttribute(STR_RESULTADO, "");
                return String.format(STR_REDIRECT_SENTINEQUERYFILESFILTER, filtroListarArchivosdto.getId());
            }
            else{
                logger.info("Error Message en readerror");
                logger.info(request1.errormessage);
                String jsonArray = request1.output;

                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();
                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                        Iterator<String> keysint = jsonObjectForKey.keys();
                        while (keysint.hasNext()) {
                            logger.info("Key segundo nivel");
                            String keyint = keysint.next();
                            logger.info("Key {} , value {} ",keyint , jsonObjectForKey.get(keyint));
                            if (keyint.equals("message")){
                                strErrorMessage =  jsonObjectForKey.get(keyint).toString();
                            }

                        }
                    }
                }
                interfazConPantalla.addAttribute(STR_ERRORMESSAGE, strErrorMessage);
                return STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO;
            }

        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            return STR_REDIRECT_SENTINELQUERYFILES;
        }
    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/checkpolygosize")
    public String checkpolygosize( @ModelAttribute(name ="consulta") ListarArchivosDto listarArchivosDto,
                                 Model interfazConPantalla) throws JSONException {

        logger.info("En /api/checkpolygosize post");
        //Objeto para guardar el filtro de la consulta
        FiltroListarArchivosDto filtroListarArchivosDto = new FiltroListarArchivosDto();
        //Mensaje de error
        String strErrorMessage = "";
        //componemos la url

        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/checkpolygosize/";

        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());
        logger.info("Post pantalla de busqueda 22");
        //Comprobamos si hay usuario logeado
        if (superCustomerUserDetails.getUsername().equals("anonimo@anonimo")) {
            listarArchivosDto.setUserName(superCustomerUserDetails.getUsername());
            listarArchivosDto.setGroupid(0L);
            listarArchivosDto.setUserid(0L);
        } else {
            logger.info("Post pantalla de busqueda 30");

            listarArchivosDto.setUserName(superCustomerUserDetails.getUsuario().getEmail());
            listarArchivosDto.setGroupid(superCustomerUserDetails.getUsuario().getGrupoTrabajo().getId());
            listarArchivosDto.setUserid(superCustomerUserDetails.getUsuario().getId());

        }
        logger.info("Post pantalla de busqueda 40");
        //Obtenemos el id del usuario y el grupo
        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put("userName", listarArchivosDto.getUserName());
            requestParam.put(STR_GROUPID, listarArchivosDto.getGroupid());
            requestParam.put(STR_USERID, listarArchivosDto.getUserid());
            requestParam.put(STR_REFERENCE, listarArchivosDto.getReference());
            requestParam.put(STR_DATEINI, listarArchivosDto.getDateIni());
            requestParam.put(STR_DATEFIN, listarArchivosDto.getDateFin());
            requestParam.put(STR_POLYGON, listarArchivosDto.getPolygon());
            requestParam.put(STR_CLOUDCOVER, listarArchivosDto.getCloudCover());
            //Se guardan los datos para almacenar el filtro de la consulta
            filtroListarArchivosDto.setReference(listarArchivosDto.getReference());
            filtroListarArchivosDto.setPolygon(listarArchivosDto.getPolygon());
            filtroListarArchivosDto.setCloudCover(listarArchivosDto.getCloudCover());
            filtroListarArchivosDto.setDateIni(listarArchivosDto.getDateIni());
            filtroListarArchivosDto.setDateFin(listarArchivosDto.getDateFin());
            filtroListarArchivosDto.setNunberOfResults(0);
            //Con el id tengo que buscar el registro a nivel de entidad
            filtroListarArchivosDto.setUsuariofiltro(superCustomerUserDetails.getUsuario());
            //Guardamos el filtro
            FiltroListarArchivosDto filtroListarArchivosDto1= callApiSenc4farmingService.getFiltroListarArchivosService().
                    guardar(filtroListarArchivosDto);
            //Comprobamos el patron
            //Se invoca a la URL
            Request request1 = new Request(urltext, requestParam, 0.1F);
            logger.info(request1.output);
            logger.info(request1.errormessage);
            if (request1.errormessage.equals("")) {
                logger.info("Post pantalla de busqueda llamada realizada: {} ", request1.output);
                String jsonArray = request1.output;
                //aqui hay que cambiar
                return String.format(STR_REDIRECT_SENTINEQUERYFILESFILTER, filtroListarArchivosDto1.getId());
            }
            else{
                logger.info("Error Message en readerror");
                logger.info(request1.errormessage);
                String jsonArray = request1.output;
                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();
                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                        Iterator<String> keysint = jsonObjectForKey.keys();
                        while (keysint.hasNext()) {
                            logger.info("Key segundo nivel");
                            String keyint = keysint.next();
                            logger.info("Key : {} , value {}" ,keyint , jsonObjectForKey.get(keyint));
                            if (keyint.equals("message")){
                                strErrorMessage =  jsonObjectForKey.get(keyint).toString();
                            }

                        }
                    }
                }
                //aqui hay que cambiar
                interfazConPantalla.addAttribute(STR_ERRORMESSAGE, strErrorMessage);
                return STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO;
            }

        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            //aqui hay que cambiar
            return STR_REDIRECT_SENTINELQUERYFILES;
        }
    }



    private Pageable createPageRequestUsing(int page, int size) {
        return PageRequest.of(page, size);
    }

    private  Listfiles findfilerecord( String key){
        Listfiles listfilesini = new Listfiles();
        listfilesini.setKey(-1);
        for(Listfiles p : objlistfiles){
            if ( p.getKey().equals( Integer.parseInt(key)) ){
                listfilesini =  p;
            }
        }

        return listfilesini;
    }
    private void setlistfilesfield(String key, JSONObject jsonObject1, String keyint, Listfiles listfilesItm
                                   , Integer option) {
        switch (key.toLowerCase()) {
            case STR_ID:
                listfilesItm.setId(jsonObject1.get(keyint).toString());
                break;
            case "name":
                listfilesItm.setName(jsonObject1.get(keyint).toString());
                break;
            case "s3path":
                listfilesItm.setS3Path(jsonObject1.get(keyint).toString());
                break;
            case "modificationdate":
                listfilesItm.setModificationDate(jsonObject1.get(keyint).toString());
                break;
            case "online":
                listfilesItm.setOnline(jsonObject1.get(keyint).toString());
                break;
            case "origindate":
                listfilesItm.setOriginDate(jsonObject1.get(keyint).toString());
                break;
            case "publicationdate":
                listfilesItm.setPublicationDate(jsonObject1.get(keyint).toString());
                break;
            case STR_REFERENCE:
                listfilesItm.setReference(jsonObject1.get(keyint).toString());
                break;
            case STR_USERID:
                listfilesItm.setUserid(jsonObject1.get(keyint).toString());
                break;
            case STR_GROUPID:
                listfilesItm.setGroupid(jsonObject1.get(keyint).toString());
                break;
            case "footprint":
                listfilesItm.setFootprint(jsonObject1.get(keyint).toString());
                break;
            case STR_GEOFOOTPRINT:
                listfilesItm.setGeofootprint(jsonObject1.get(keyint).toString());
                break;
            default:
                break;

        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objlistfiles.add(listfilesItm);

        }else {
            //el elemennto no existe y se añadeç
            listfilesItm.setKey( Integer.parseInt(keyint));
            objlistfiles.add(listfilesItm);
        }

    }

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/downloadbands/{idquery}")
    public String listfilesDownloadbands(@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) throws Exception {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = callApiSenc4farmingService.getSentinelQueryFilesService().
                getRepo().findById(id);
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
        Object token = session.getAttribute(STR_SEESIONACCESSTOKEN);
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
                requestParam.put(STRTOKEN,token);
                //Comprobamos el patron
                //Se invoca a la URL
                Request request1 = new Request(urltext, requestParam);
                logger.info(request1.output);

                String jsonArray = request1.output;

                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();

                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                        Iterator<String> keysint = jsonObjectForKey.keys();
                        while (keysint.hasNext()) {
                            String keyint = keysint.next();
                            Listfilestiff itemlistfilesCheck = findfiletiffrecord(keyint);
                            if (itemlistfilesCheck.getKey().equals(-1)) {
                                Listfilestiff itmlistfilesnew = new Listfilestiff();
                                setlistfilestifffield(key, jsonObjectForKey, keyint, itmlistfilesnew, 0);
                            } else {
                                // You use this ".get()" method to actually get your Listfiles from the Optional object
                                objlistfilestiff.remove(itemlistfilesCheck);
                                setlistfilestifffield(key, jsonObjectForKey, keyint, itemlistfilesCheck, 1);
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
                callApiSenc4farmingService.getSentinelQueryFilesTiffService().getRepo().
                        deleteSentinelQueryFilesTiffBySentinelQueryFilesfortiff_Id(sentinelQueryFiles1.getId());

                if (!objlistfilestiff.isEmpty()) {
                    //Guardamos los datos
                    callApiSenc4farmingService.getSentinelQueryFilesService().
                            getRepo().save(sentinelQueryFiles1);


                    //Guardamos desde la lista
                    callApiSenc4farmingService.getSentinelQueryFilesTiffService().
                            guardarDesdeConsulta(objlistfilestiff, sentinelQueryFiles1.getId());

                    return String.format(STR_REDIRECT_SENTINEQUERYFILESFILTER, sentinelQueryFiles.get().getId());

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

    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @GetMapping ("/api/listfiles/downloadbands/{idquery}")
    public String listfilesDownloadbandsGet (@PathVariable("idquery") Integer id, Model interfazConPantalla,HttpSession session) throws Exception {
        //Objeto para guardar el filtro de la consulta
        Optional<SentinelQueryFiles> sentinelQueryFiles = callApiSenc4farmingService.getSentinelQueryFilesService().
                getRepo().findById(id);
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
        Object token =  session.getAttribute(STR_SEESIONACCESSTOKEN);
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
                //Se invoca a la URL
                Request request1 = new Request(urltext, requestParam);
                String jsonArray = request1.output;

                JSONObject jsonObject = new JSONObject(jsonArray);
                Iterator<String> keys = jsonObject.keys();

                while (keys.hasNext()) {
                    String key = keys.next();
                    if (jsonObject.get(key) instanceof JSONObject) {
                        // do something with jsonObject here
                        JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                        Iterator<String> keysint = jsonObjectForKey.keys();
                        while (keysint.hasNext()) {
                            String keyint = keysint.next();
                            Listfilestiff itemlistfilesCheck = findfiletiffrecord(keyint);
                            if (itemlistfilesCheck.getKey().equals(-1)) {
                                Listfilestiff itmlistfilesnew = new Listfilestiff();
                                setlistfilestifffield(key, jsonObjectForKey, keyint, itmlistfilesnew, 0);
                            } else {
                                // You use this ".get()" method to actually get your Listfiles from the Optional object
                                logger.info(" /api/listfiles/downloadbands get valores para el json existe indice");

                                objlistfilestiff.remove(itemlistfilesCheck);
                                setlistfilestifffield(key, jsonObjectForKey, keyint, itemlistfilesCheck, 1);
                            }
                        }
                    }
                }
                if (objlistfilestiff.isEmpty())
                    sentinelQueryFiles1.setNunberOfTiff(0);
                else
                    sentinelQueryFiles1.setNunberOfTiff(objlistfilestiff.size());

                //Eliminamos los resultados de la consulta anterior por referencia
                logger.info("Eliminando datos sentinelQueryFilesTiffService");
                callApiSenc4farmingService.getSentinelQueryFilesTiffService().getRepo().
                        deleteSentinelQueryFilesTiffBySentinelQueryFilesfortiff_Id(sentinelQueryFiles1.getId());

                if (!objlistfilestiff.isEmpty()) {
                    //Guardamos los datos
                    logger.info("Eliminando datos sentinelQueryFilesService");
                    callApiSenc4farmingService.getSentinelQueryFilesService().getRepo().save(sentinelQueryFiles1);


                    //Guardamos desde la lista
                    logger.info("Eliminando datos sentinelQueryFilesTiffService");
                    callApiSenc4farmingService.getSentinelQueryFilesTiffService().
                            guardarDesdeConsulta(objlistfilestiff, sentinelQueryFiles1.getId());

                    return String.format(STR_REDIRECT_SENTINEQUERYFILESFILTER, sentinelQueryFiles.get().getId());

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
        } else{
            interfazConPantalla.addAttribute(STR_CONSULTA,copernicuscredentials);
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
            case STR_BAND:
                listfilesItm.setBand(jsonObject1.get(keyint).toString());
                break;
            case STR_PATH:
                listfilesItm.setPath(jsonObject1.get(keyint).toString());
                break;
            default:
                listfilesItm.setPath("");
                break;

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
    private void setlistfilesevalscriptfield(String key, JSONObject jsonObject1, String keyint,
                 ListfilesEvalScript listfilesItm  , Integer option) {
        if  (key.equalsIgnoreCase(STR_PATH)) {
                listfilesItm.setPath(jsonObject1.get(keyint).toString());
        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objlistfilesevalscript.add(listfilesItm);

        }else {
            //el elemennto no existe y se añadeç
            listfilesItm.setKey( Integer.parseInt(keyint));
            objlistfilesevalscript.add(listfilesItm);
        }

    }

    /**
     *
     * @param key
     * @return
     */
    private  ListfilesEvalScript findfileevalscriptrecord( String key){
        ListfilesEvalScript listfilesini = new ListfilesEvalScript();
        listfilesini.setKey(-1);
        for (ListfilesEvalScript p : objlistfilesevalscript) {
            if (p.getKey().equals(Integer.parseInt(key))) {
                listfilesini = p;
            }
        }


        return listfilesini;
    }
    //El que con los datos de la pantalla guarda la informacion de tipo PostMapping
    @PostMapping("/api/listfiles/executeevalscript")
    public String executeevalscript(@ModelAttribute(name ="datosscript") EvalScriptDto dtoEvalscript,
                                    @ModelAttribute(name ="datos") EvalScriptLaunchDto evalScriptLaunchDtoIn,
                                    Model interfazConPantalla,HttpSession session) throws JSONException {

        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        //Instancia en memoria del dto a informar en la pantalla
        Copernicuscredentials copernicuscredentials = new Copernicuscredentials();
        //Check if credentials exists
        Object cliId = session.getAttribute(STRCLIENTID);
        Object secret = session.getAttribute(STRSECRET);
        Object token =  session.getAttribute(STR_SEESIONACCESSTOKEN);
        if (cliId != null){
            copernicuscredentials.setClientid((String) cliId);
            copernicuscredentials.setSecret((String) secret);
            copernicuscredentials.setToken((String) token);
            //componemos la url
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/sentinel/executeevalscript/";
            //Obtenemos el id del usuario y el grupo
            Optional<EvalScript> evalScript = callApiSenc4farmingService.getEvalScriptService().encuentraPorIdEntity(dtoEvalscript.getId());
            if (evalScript.isPresent()){
                evalScriptLaunchDtoIn.setEvalScript(evalScript.get());
                EvalScriptLaunchDto  evalScriptLaunchDto = callApiSenc4farmingService.getEvalScriptLaunchService().
                        guardar(evalScriptLaunchDtoIn);
                try {
                    JSONObject requestParam = new JSONObject();
                    requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                    requestParam.put(STR_QUERYID, evalScriptLaunchDto.getId());
                    requestParam.put(STR_OFFSET, evalScriptLaunchDto.getOfsset());
                    requestParam.put(STR_DATEINI, evalScriptLaunchDto.getDateIni());
                    requestParam.put(STR_DATEFIN, evalScriptLaunchDto.getDateFin());
                    requestParam.put(STR_POLYGON,  evalScriptLaunchDto.getPolygon());
                    requestParam.put("collection",  evalScriptLaunchDto.getCollection());
                    requestParam.put(STRCLIENTID,  copernicuscredentials.getClientid());
                    requestParam.put(STRSECRET,  copernicuscredentials.getSecret());
                    requestParam.put(STRTOKEN,  copernicuscredentials.getToken());
                    requestParam.put("maxcloudcoverage",  evalScriptLaunchDto.getMaxcloudcoverage());
                    requestParam.put("script",  dtoEvalscript.getScriptText());
                    requestParam.put("resolution", evalScriptLaunchDto.getResolution());

                    //Comprobamos el patron
                    //Se invoca a la URL
                    Request request1 = new Request(urltext, requestParam);
                    String jsonArray = request1.output;

                    JSONObject jsonObject = new JSONObject(jsonArray);
                    Iterator<String> keys = jsonObject.keys();

                    while (keys.hasNext()) {
                        String key = keys.next();
                        if (jsonObject.get(key) instanceof JSONObject) {
                            // do something with jsonObject here
                            JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                            Iterator<String> keysint = jsonObjectForKey.keys();
                            while (keysint.hasNext()) {
                                String keyint = keysint.next();
                                ListfilesEvalScript itemlistfilesevalscriptCheck = findfileevalscriptrecord(keyint);
                                if (itemlistfilesevalscriptCheck.getKey().equals(-1)) {
                                    ListfilesEvalScript itemlistfilesevalscript = new ListfilesEvalScript();
                                    setlistfilesevalscriptfield(key, jsonObjectForKey, keyint, itemlistfilesevalscript, 0);
                                } else {
                                    // You use this ".get()" method to actually get your Listfiles from the Optional object
                                    objlistfilesevalscript.remove(itemlistfilesevalscriptCheck);
                                    setlistfilesevalscriptfield(key, jsonObjectForKey, keyint, itemlistfilesevalscriptCheck, 1);
                                }
                            }
                        }
                    }



                    if (!objlistfilesevalscript.isEmpty()){
                        //Actualizamos el path
                        evalScriptLaunchDto.setPathtiff(objlistfilesevalscript.get(0).getPath());
                        evalScriptLaunchDto.setPathjson(objlistfilesevalscript.get(1).getPath());
                        //guardamos los datos
                        EvalScriptLaunchDto evalScriptLaunchDto1 = callApiSenc4farmingService.getEvalScriptLaunchService().
                                guardar(evalScriptLaunchDto);
                        interfazConPantalla.addAttribute(STR_CONSULTA,evalScriptLaunchDto1);

                        return "evalscript/launchresultados";
                    }
                    else {

                        return STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO;
                    }

                } catch (Exception e) {
                    logger.info(STR_ERRORMSG);
                    logger.info(e.getClass().getSimpleName());
                    logger.info(e.getMessage());
                    interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                    return "redirect:/evalscript";
                }
            } else {
                return STR_SENTINELQUERYFILES_DETALLES_NO_ENCONTRADO;
            }


        } else {
            interfazConPantalla.addAttribute(STR_CONSULTA,copernicuscredentials);
            return STR_REDIRECT_API_CREDENTIALS;
        }
    }


    @GetMapping("/api/csvdata")
    public String csvdataGet(ModelMap interfazConPantalla) {
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/csvdatosprocesados/";
        Request  request1 = new Request(urltext);
        EscribeCSVDto  escribeCSVDto = new EscribeCSVDto();
        try {
            escribeCSVDto.setResultado(request1.output);
            interfazConPantalla.addAttribute("file",escribeCSVDto);
        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            escribeCSVDto.setResultado(STR_ERRORMSG + e.getClass().getSimpleName() +  e.getMessage());
            interfazConPantalla.addAttribute("file",escribeCSVDto );
        }
        return "api/obtenercsv";
    }
    @PostMapping("/api/csvdata")
    public String csvdataPost(@ModelAttribute(name ="file") EscribeCSVDto escribeCSVDto,Model interfazConPantalla) throws IOException {


        File file = new File(escribeCSVDto.getRuta(),escribeCSVDto.getNombrearchivo());
        try (FileWriter fileWriter = new FileWriter(file)){
            if (escribeCSVDto.getNombrearchivo().length() > 5 && escribeCSVDto.getRuta().length() > 4) {
                logger.info("long cadena");
                logger.info(escribeCSVDto.getResultado().length());
                fileWriter.write(escribeCSVDto.getResultado());
                interfazConPantalla.addAttribute(STR_RESULTADO, "El archivo se ha guardado correctamente ");
            } else {
                interfazConPantalla.addAttribute(STR_RESULTADO, "El nombre del archivo o la ruta no son correctos ");
            }

        } catch (Exception e) {
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
        }
        return "api/obtenercsvresultado";
    }

    /**
     *
     * @param key
     * @return
     */
    private DatosLucas2018Api finddatoslucas2018OCrecord(String key){
        DatosLucas2018Api listini = new DatosLucas2018Api();
        listini.setKeyapi(-1);
        for (DatosLucas2018Api p : objlistdatoslucas2018Api) {
            if (p.getKeyapi().equals(Integer.parseInt(key))) {
                listini = p;
            }
        }
        return listini;
    }
    private void setlistdatoslucas2018OCfield(String key, JSONObject jsonObject1, String keyint,
                                              DatosLucas2018Api listItm  , Integer option) {
        switch (key.toLowerCase()) {
            case STR_LONGITUD:
                listItm.setLongitud(jsonObject1.get(keyint).toString());
                break;
            case STR_LATITUD:
                listItm.setLatitud(jsonObject1.get(keyint).toString());
                break;
            case STR_ID:
                listItm.setId(jsonObject1.get(keyint).toString());
                break;
            case STR_PATH:
                listItm.setPath(jsonObject1.get(keyint).toString());
                break;
            case STR_REFLECTANCE:
                listItm.setReflectance(jsonObject1.get(keyint).toString());
                break;
            case STR_BAND:
                listItm.setBand(jsonObject1.get(keyint).toString());
                break;
            case STR_SURVEY_DATE:
                listItm.setSurvey_date(jsonObject1.get(keyint).toString());
                break;
            case STR_OC:
                listItm.setOc(jsonObject1.get(keyint).toString());
                break;
            case STR_KEY:
                listItm.setKeyapi(Integer.valueOf(keyint));
                break;
            default:
                listItm.setKeyapi(0);
                break;
        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objlistdatoslucas2018Api.add(listItm);

        }else {
            //el elemennto no existe y se añadeç
            listItm.setKeyapi( Integer.parseInt(keyint));
            objlistdatoslucas2018Api.add(listItm);
        }

    }
    public Page<DatosLucas2018Api> getLucas2018OCpages(int page, int size) {

        Pageable pageRequest = createPageRequestUsing(page, size);

        List<DatosLucas2018Api> all = objlistdatoslucas2018Api;
        int start = (int) pageRequest.getOffset();
        int end = Math.min((start + pageRequest.getPageSize()), all.size());

        List<DatosLucas2018Api> pageContent = all.subList(start, end);
        return new PageImpl<>(pageContent, pageRequest, all.size());
    }

    @GetMapping ("/api/lucas/lucas2018Search")
    public String lucas2018list (@ModelAttribute(name ="datos") DatosLucasSearchDto datosLucasSEarchDto,
                                 Model interfazConPantalla){
        DatosLucasSearchDto datosLucasSearchDto = new DatosLucasSearchDto();
        interfazConPantalla.addAttribute(STR_DATOS,datosLucasSearchDto);
        return "lucas/search";
    }
    @GetMapping ("/api/lucas/lucas2018Export")
    public ResponseEntity<byte[]> lucas2018listCsvFile (@ModelAttribute(name ="datos") DatosLucasSearchDto datosLucasSEarchDto,
                                                        Model interfazConPantalla){
        logger.info("lucas2018listCsvFile: paso1");

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDispositionFormData("attachment", "DatosLucas2018Api.csv");
        logger.info("lucas2018listCsvFile: paso3");
        byte[] csvBytes = csvGeneratorUtil.generateCsv(objlistdatoslucas2018Api).getBytes();
        return new ResponseEntity<>(csvBytes, headers, HttpStatus.OK);
    }
    @GetMapping ("/api/uploadedfiles/uploadCsvExport/{id}")
    public ResponseEntity<byte[]> csvuserFile (@PathVariable(STR_ID) Integer id,
                                               Model interfazConPantalla){
        logger.info("csvuserFile: paso1");
        List<DatosUploadCsvDto> lstdatosUploadCsvDto = callApiSenc4farmingService.getDatosUploadCsvService().
                getUploadedCsvDataSearchId(id);
        String filename =  "csvreflectance_" + id + ".csv";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDispositionFormData("attachment", filename);
        logger.info("csvuserFile: paso3");
        byte[] csvBytes = csvGeneratorUtil.generateUploadedCsvdatos(lstdatosUploadCsvDto).getBytes();
        return new ResponseEntity<>(csvBytes, headers, HttpStatus.OK);
    }
    @PostMapping ("/api/lucas/lucas2018list")
    public String lucas2018list (@ModelAttribute(name ="datos") DatosLucasSearchDto datosLucasSEarchDto,
                                 Model interfazConPantalla,HttpSession session)  throws JSONException{
        //componemos la url
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/obtenerlucas2018proc/";
        //Obtenemos los datos del usuario de la sesión

        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());


        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
            requestParam.put(STR_DATEINI, datosLucasSEarchDto.getDateIni());
            requestParam.put(STR_DATEFIN, datosLucasSEarchDto.getDateFin());
            requestParam.put(STR_POLYGON, datosLucasSEarchDto.getPolygon());
            requestParam.put("ref", "lucas2018OCND");
            //Comprobamos el patron
            //Se invoca a la URL
            Request request1 = new Request(urltext, requestParam);
            String jsonArray = request1.output;
            JSONObject jsonObject = new JSONObject(jsonArray);
            Iterator<String> keys = jsonObject.keys();

            while (keys.hasNext()) {
                String key = keys.next();
                if (jsonObject.get(key) instanceof JSONObject) {
                    // do something with jsonObject here
                    JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                    Iterator<String> keysint = jsonObjectForKey.keys();
                    while (keysint.hasNext()) {
                        String keyint = keysint.next();
                        DatosLucas2018Api itemlistCheck = finddatoslucas2018OCrecord(keyint);
                        if (itemlistCheck.getKeyapi().equals(-1)) {
                            setlistdatoslucas2018OCfield(key, jsonObjectForKey, keyint, itemlistCheck, 0);
                        } else {
                            // You use this ".get()" method to actually get your Listfiles from the Optional object
                            objlistdatoslucas2018Api.remove(itemlistCheck);
                            setlistdatoslucas2018OCfield(key, jsonObjectForKey, keyint, itemlistCheck, 1);
                        }
                    }
                }
            }

            //id unico de la busqueda
            int low = 10;
            int high = 1000000;
            int result = r.nextInt(high-low) + low;
            //comprobamos si hay datos
            if (!objlistdatoslucas2018Api.isEmpty()){
                //Guardamos los datos en la tabla
                Iterator<DatosLucas2018Api> it = objlistdatoslucas2018Api.iterator();
                List<DatosLucas2018Dto> lstdatosLucas2018Dto = new ArrayList<>();
                // mientras al iterador queda proximo juego
                while(it.hasNext()){
                    //Obtenemos la password de a entidad
                    //Datos del usuario
                    DatosLucas2018Dto dto = new DatosLucas2018Dto();
                    DatosLucas2018Api dtoapi =  it.next();

                    dto.setSearchid(result);
                    dto.setBand(dtoapi.getBand());
                    dto.setPointid(dtoapi.getId());
                    dto.setPath(dtoapi.getPath());
                    dto.setReflectance(dtoapi.getReflectance());
                    dto.setLatitud(dtoapi.getLatitud());
                    dto.setLongitud(dtoapi.getLongitud());
                    dto.setKeyapi(dtoapi.getKeyapi());
                    dto.setOc(dtoapi.getOc());
                    dto.setSsurveyDate(dtoapi.getSurvey_date());


                    DatosLucas2018Dto dtosaved = callApiSenc4farmingService.getDatosLucas2018Service().guardar(dto);
                    lstdatosLucas2018Dto.add(dtosaved);
                }
                //Ordenamos la lista
                List<DatosLucas2018Dto> sortedItems = lstdatosLucas2018Dto.stream()
                        .sorted(Comparator.comparing(DatosLucas2018Dto::getBand))
                        .sorted(Comparator.comparing(DatosLucas2018Dto::getPointid))
                        .toList();
                callApiSenc4farmingService.getDatosLucas2018Service().guardar(sortedItems);
                //Asigno atributos para kalman y muestro
                FiltroConsultaKalmanDto dtofiltroConsultaKanlam = new FiltroConsultaKalmanDto();
                dtofiltroConsultaKanlam.setCsvid(-1);
                dtofiltroConsultaKanlam.setUserid(superCustomerUserDetails.getUserID());
                dtofiltroConsultaKanlam.setDirstr(configuationProperties.getKalmandistr());
                dtofiltroConsultaKanlam.setOffset(0.01);
                dtofiltroConsultaKanlam.setCloudCover(5);
                dtofiltroConsultaKanlam.setNumDaysSerie(60);
                dtofiltroConsultaKanlam.setNumberOfGeeImages(5);
                dtofiltroConsultaKanlam.setPath("N/A");
                dtofiltroConsultaKanlam.setOrigin("lucas");
                //Grabamos antes de enviar
                FiltroConsultaKalmanDto filtroConsultaKalmanDto =   callApiSenc4farmingService.getFiltroConsultaKalmanService()
                        .guardar(dtofiltroConsultaKanlam);
                List<DatosLucas2018Dto> datosLucas2018Dtos =callApiSenc4farmingService.getDatosLucas2018Service()
                        .getlucasfloat(result,"%FLOAT32%");
                interfazConPantalla.addAttribute(STR_LISTA, datosLucas2018Dtos);
                interfazConPantalla.addAttribute("filtro",filtroConsultaKalmanDto);
                return "lucas/lista";
            }
            else {
                return STR_LUCAS_DETALLES_NO_ENCONTRADO;
            }

        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            return STR_LUCAS_DETALLES_NO_ENCONTRADO;
        }
    }

    @GetMapping ("/api/uploadedfiles/csv/reflvectors/copsh/{opt}/{id}")
    public String csvreflvectors (@PathVariable(STR_ID) Integer id,@PathVariable("opt")Integer opt,Model interfazConPantalla,HttpSession session) {
        //Buscamos los datos del archivo csv en la bbdd
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        if (optuploadedFilesDto.isPresent()) {
            //componemos la url
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/obtenercsvproc/reflvector/copsh/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());


            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, "landstat");
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, "sentinel");
                }
                requestParam.put(STR_PATH, optuploadedFilesDto.get().getPath()+"/"+optuploadedFilesDto.get().getDescription());
                //Comprobamos el patron
                //Se invoca a la URL
                Request request1 = new Request(urltext, requestParam);
                logger.info("/api/uploadedfiles/csv/reflvectors/copsh/: Post pantalla de busqueda 60");
                String jsonArray = request1.output;
                logger.info("/api/uploadedfiles/csv/reflvectors/copsh/: Post pantalla de busqueda 80");
                jsonlistdatosuploadcsvOCfield(jsonArray);

                logger.info("/api/uploadedfiles/csv/reflvectors/copsh/: Post pantalla de busqueda 100");
                //id unico de la busqueda
                int low = 10;
                int high = 1000000;
                int result = r.nextInt(high - low) + low;
                //comprobamos si hay datos
                if (!objlistdatosuploadcsvApi.isEmpty()) {
                    logger.info("/api/uploadedfiles/csv/reflvectors/copsh/: Post pantalla de busqueda 110");
                    //Guardamos los datos en la tabla
                    Iterator<DatosUploadCsvApi> it = objlistdatosuploadcsvApi.iterator();
                    List<DatosUploadCsvDto> lstdatosUploadCsvDto = new ArrayList<>();
                    // mientras al iterador queda proximo juego
                    while (it.hasNext()) {
                        //Obtenemos la password de a entidad
                        //Datos del usuario
                        logger.info("Encuentro elemento");
                        DatosUploadCsvDto dto = new DatosUploadCsvDto();
                        DatosUploadCsvApi dtoapi = it.next();
                        logger.info("Iterador leigo id:");
                        logger.info(dtoapi.getId());
                        dto.setSearchid(result);
                        dto.setBand(dtoapi.getBand());
                        dto.setPointid(dtoapi.getId());
                        dto.setPath(dtoapi.getPath());
                        dto.setUserid(dtoapi.getUserid());
                        dto.setReflectance(dtoapi.getReflectance());
                        dto.setLatitud(dtoapi.getLatitud());
                        dto.setLongitud(dtoapi.getLongitud());
                        dto.setKeyapi(dtoapi.getKeyapi());
                        dto.setOc(dtoapi.getOc());
                        dto.setSurveyDate(dtoapi.getSurveyDate());
                        logger.info("Iterador leigo y antes de guardado id:");
                        logger.info(dto.getPointid());

                        DatosUploadCsvDto dtosaved = callApiSenc4farmingService.getDatosUploadCsvService().guardar(dto);
                        logger.info("Encuentro elemento guardado");
                        logger.info(dtosaved.getId());
                        logger.info(dtosaved.getPointid());
                        lstdatosUploadCsvDto.add(dtosaved);
                    }
                    //Ordenamos la lista
                    List<DatosUploadCsvDto> sortedItems = lstdatosUploadCsvDto.stream()
                            .sorted(Comparator.comparing(DatosUploadCsvDto::getBand))
                            .sorted(Comparator.comparing(DatosUploadCsvDto::getPointid))
                            .toList();
                    logger.info("elementos de la lista sortedItems");
                    logger.info(sortedItems.size());
                    callApiSenc4farmingService.getDatosUploadCsvService().guardar(sortedItems);

                    logger.info("result" );
                    logger.info(result);
                    List<DatosUploadCsvDto> datosUploadCsvDtos = callApiSenc4farmingService.getDatosUploadCsvService()
                            .getUploadedCsvData(result,optuploadedFilesDto.get().getPath());
                    interfazConPantalla.addAttribute(STR_LISTA, sortedItems);
                    interfazConPantalla.addAttribute("idres",result);
                    logger.info("elementos de la lista");
                    logger.info(datosUploadCsvDtos.size());
                    return "upload/listareflvectors";
                } else {
                    logger.info("/api/uploadedfiles/csv/reflvectors/copsh/: Post pantalla de busqueda 210");
                    return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
                }

            } catch (Exception e) {
                logger.warn(STR_ERRORMSG);
                logger.warn(e.getClass().getSimpleName());
                logger.warn(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
            }
        }
        else{
            return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
        }
    }
    private  void jsonlistdatosuploadcsvOCfield(String jsonArray){
        try {
            JSONObject jsonObject = new JSONObject(jsonArray);
            Iterator<String> keys = jsonObject.keys();

            while (keys.hasNext()) {
                String key = keys.next();
                if (jsonObject.get(key) instanceof JSONObject) {
                    // do something with jsonObject here
                    JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                    Iterator<String> keysint = jsonObjectForKey.keys();
                    while (keysint.hasNext()) {
                        String keyint = keysint.next();
                        DatosUploadCsvApi itemlistCheck = finddatosuploadcsvOCrecord(keyint);
                        if (itemlistCheck.getKeyapi().equals(-1)) {
                            setlistdatosuploadcsvOCfield(key, jsonObjectForKey, keyint, itemlistCheck, 0);
                        } else {
                            // You use this ".get()" method to actually get your Listfiles from the Optional object
                            logger.info("/api/uploadedfiles/csv/reflvectors/copsh/ post   valores para el json existe indice");

                            objlistdatosuploadcsvApi.remove(itemlistCheck);
                            setlistdatosuploadcsvOCfield(key, jsonObjectForKey, keyint, itemlistCheck, 1);
                        }
                    }
                }
            }
        } catch (JSONException err) {
            logger.error(STR_ERROR,  err.toString());
            throw err;
        }
    }

    @GetMapping ("/api/uploadedfiles/csv/reflvectors/gee/{opt}/{id}")
    public String csvReflVectorsGee (@PathVariable(STR_ID) Integer id,@PathVariable("opt")Integer opt, Model interfazConPantalla,HttpSession session)  {
        //Buscamos los datos del archivo csv en la bbdd
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()) {
            //componemos la url
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/obtenercsvproc/reflvector/gee/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());


            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                if (opt == 1){
                    requestParam.put(STR_SATELLITE, "landstat");
                }else if (opt == 2)
                {
                    requestParam.put(STR_SATELLITE, "sentinel");
                }
                requestParam.put(STR_PATH, optuploadedFilesDto.get().getPath()+"/"+optuploadedFilesDto.get().getDescription());
                //Comprobamos el patron
                //Se invoca a la URL
                logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 50");
                Request request1 = new Request(urltext, requestParam);
                logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 60");
                String jsonArray = request1.output;
                logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 80");
                jsonDatosuploadcsvOCrecord(jsonArray);
                logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 100");
                //id unico de la busqueda

                int low = 10;
                int high = 1000000;
                int result = r.nextInt(high - low) + low;
                //comprobamos si hay datos
                if (!objlistdatosuploadcsvApi.isEmpty()) {
                    logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 110");
                    //Guardamos los datos en la tabla
                    Iterator<DatosUploadCsvApi> it = objlistdatosuploadcsvApi.iterator();
                    List<DatosUploadCsvDto> lstdatosUploadCsvDto = new ArrayList<>();
                    // mientras al iterador queda proximo juego
                    while (it.hasNext()) {
                        //Obtenemos la password de a entidad
                        //Datos del usuario
                        logger.info("Encuentro elemento");
                        DatosUploadCsvDto dto = new DatosUploadCsvDto();
                        DatosUploadCsvApi dtoapi = it.next();
                        logger.info("Iterador leigo id:");
                        logger.info(dtoapi.getId());
                        dto.setSearchid(result);
                        dto.setBand(dtoapi.getBand());
                        dto.setPointid(dtoapi.getId());
                        dto.setPath(dtoapi.getPath());
                        dto.setUserid(dtoapi.getUserid());
                        dto.setReflectance(dtoapi.getReflectance());
                        dto.setLatitud(dtoapi.getLatitud());
                        dto.setLongitud(dtoapi.getLongitud());
                        dto.setKeyapi(dtoapi.getKeyapi());
                        dto.setOc(dtoapi.getOc());
                        dto.setSurveyDate(dtoapi.getSurveyDate());
                        logger.info("Iterador leigo y antes de guardado id:");
                        logger.info(dto.getPointid());

                        DatosUploadCsvDto dtosaved = callApiSenc4farmingService.getDatosUploadCsvService().guardar(dto);
                        logger.info("Encuentro elemento guardado");
                        logger.info(dtosaved.getId());
                        logger.info(dtosaved.getPointid());
                        lstdatosUploadCsvDto.add(dtosaved);
                    }
                    //Ordenamos la lista
                    List<DatosUploadCsvDto> sortedItems = lstdatosUploadCsvDto.stream()
                            .sorted(Comparator.comparing(DatosUploadCsvDto::getBand))
                            .sorted(Comparator.comparing(DatosUploadCsvDto::getPointid))
                            .toList();
                    logger.info("elementos de la lista sortedItems");
                    logger.info(sortedItems.size());
                    callApiSenc4farmingService.getDatosUploadCsvService().guardar(sortedItems);

                    logger.info("result" );
                    logger.info(result);
                    List<DatosUploadCsvDto> datosUploadCsvDtos = callApiSenc4farmingService.getDatosUploadCsvService()
                            .getUploadedCsvData(result,optuploadedFilesDto.get().getPath());
                    interfazConPantalla.addAttribute(STR_LISTA, sortedItems);
                    interfazConPantalla.addAttribute("idres",result);
                    logger.info("elementos de la lista");
                    logger.info(datosUploadCsvDtos.size());
                    return "upload/listareflvectors";
                } else {
                    logger.info("/api/uploadedfiles/csv/reflvectors/gee/: Post pantalla de busqueda 210");
                    return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
                }

            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
            }
        }
        else{
            return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
        }
    }

    private void jsonDatosuploadcsvOCrecord(String jsonArray){
        try {
            JSONObject jsonObject = new JSONObject(jsonArray);
            Iterator<String> keys = jsonObject.keys();

            while (keys.hasNext()) {
                String key = keys.next();
                if (jsonObject.get(key) instanceof JSONObject) {
                    // do something with jsonObject here
                    JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                    Iterator<String> keysint = jsonObjectForKey.keys();
                    while (keysint.hasNext()) {
                        String keyint = keysint.next();
                        DatosUploadCsvApi itemlistCheck = finddatosuploadcsvOCrecord(keyint);
                        if (itemlistCheck.getKeyapi().equals(-1)) {
                            setlistdatosuploadcsvOCfield(key, jsonObjectForKey, keyint, itemlistCheck, 0);
                        } else {
                            // You use this ".get()" method to actually get your Listfiles from the Optional object
                            logger.info("/api/uploadedfiles/csv/reflvectors/gee/ post   valores para el json existe indice");

                            objlistdatosuploadcsvApi.remove(itemlistCheck);
                            setlistdatosuploadcsvOCfield(key, jsonObjectForKey, keyint, itemlistCheck, 1);
                        }
                    }
                }
            }
        } catch (JSONException err) {
            logger.info(STR_ERROR, err.toString());
        }
    }

    /**
     *
     * @param key
     * @return
     */
    private DatosUploadCsvApi finddatosuploadcsvOCrecord(String key){
        DatosUploadCsvApi listini = new DatosUploadCsvApi();
        listini.setKeyapi(-1);
        for (DatosUploadCsvApi p : objlistdatosuploadcsvApi) {
            if (p.getKeyapi().equals(Integer.parseInt(key))) {
                listini = p;
            }
        }
        return listini;
    }
    private void setlistdatosuploadcsvOCfield(String key, JSONObject jsonObject1, String keyint,
                                              DatosUploadCsvApi listItm  , Integer option) {
        switch (key.toLowerCase()) {
            case STR_LONGITUD:
                listItm.setLongitud(jsonObject1.get(keyint).toString());
                break;
            case STR_LATITUD:
                listItm.setLatitud(jsonObject1.get(keyint).toString());
                break;
            case STR_ID:
                listItm.setId(jsonObject1.get(keyint).toString());
                break;
            case STR_PATH:
                listItm.setPath(jsonObject1.get(keyint).toString());
                break;
            case "user_id":
                listItm.setUserid(jsonObject1.get(keyint).toString());
                break;
            case STR_REFLECTANCE:
                listItm.setReflectance(jsonObject1.get(keyint).toString());
                break;
            case STR_BAND:
                listItm.setBand(jsonObject1.get(keyint).toString());
                break;
            case STR_SURVEY_DATE:
                listItm.setSurveyDate(jsonObject1.get(keyint).toString());
                break;
            case STR_OC:
                listItm.setOc(jsonObject1.get(keyint).toString());
                break;
            case STR_KEY:
                listItm.setKeyapi(Integer.valueOf(keyint));
                break;
            default:
                listItm.setKeyapi(0);
                break;
        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objlistdatosuploadcsvApi.add(listItm);

        }else {
            //el elemennto no existe y se añadeç
            listItm.setKeyapi( Integer.parseInt(keyint));
            objlistdatosuploadcsvApi.add(listItm);
        }

    }
    public Page<DatosUploadCsvApi> getuploadcsvOCpages(int page, int size) {

        Pageable pageRequest = createPageRequestUsing(page, size);

        List<DatosUploadCsvApi> all = objlistdatosuploadcsvApi;
        int start = (int) pageRequest.getOffset();
        int end = Math.min((start + pageRequest.getPageSize()), all.size());

        List<DatosUploadCsvApi> pageContent = all.subList(start, end);
        return new PageImpl<>(pageContent, pageRequest, all.size());
    }


    @GetMapping ("/api/uploadedfiles/replectance/{id}")
    public String csvReflectancelist (@PathVariable(STR_ID) Integer id,Model interfazConPantalla,HttpSession session)  {
        Optional<UploadedFilesDto> optuploadedFilesDto = uploadedFilesService.encuentraPorId(id);
        logger.info("getreflecance : elemento leido");
        if (optuploadedFilesDto.isPresent()) {
            //componemos la url
            String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/obtenerreflectancecsv/";
            //Obtenemos los datos del usuario de la sesión
            SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            logger.info(superCustomerUserDetails.getUsername());


            try {
                JSONObject requestParam = new JSONObject();
                requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());
                requestParam.put("csvid", optuploadedFilesDto.get().getId());

                //Comprobamos el patron
                //Se invoca a la URL
                logger.info("Post pantalla de busqueda 50");
                Request request1 = new Request(urltext, requestParam);
                String jsonArray = request1.output;
                jsonUploadedFilesReflectancerecord(jsonArray);

                //comprobamos si hay datos
                if (!objListUploadedFilesReflectances.isEmpty()) {
                    //Se muestra el listado
                    interfazConPantalla.addAttribute(STR_LISTA, objListUploadedFilesReflectances);
                    return "upload/reflectance";
                } else {
                    return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
                }

            } catch (Exception e) {
                logger.info(STR_ERRORMSG);
                logger.info(e.getClass().getSimpleName());
                logger.info(e.getMessage());
                interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
                return STR_UPLOAD_DETALLES_NO_ENCONTRADO;
            }
        }
        else {
            return STR_LUCAS_DETALLES_NO_ENCONTRADO;
        }
    }
    private void jsonUploadedFilesReflectancerecord(String jsonArray){
        try {
            JSONObject jsonObject = new JSONObject(jsonArray);
            Iterator<String> keys = jsonObject.keys();

            while (keys.hasNext()) {
                String key = keys.next();
                if (jsonObject.get(key) instanceof JSONObject) {
                    // do something with jsonObject here
                    JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                    Iterator<String> keysint = jsonObjectForKey.keys();
                    while (keysint.hasNext()) {
                        String keyint = keysint.next();
                        logger.info("valores para el json");
                        logger.info(KEYLOG , key , keyint ,jsonObjectForKey.get(keyint));
                        UploadedFilesReflectance itemlistCheck = findUploadedFilesReflectancerecord(keyint);

                        if (itemlistCheck.getKey().equals(-1)) {
                            setUploadedFilesReflectancefield(key, jsonObjectForKey, keyint, itemlistCheck, 0);
                        } else {
                            // You use this ".get()" method to actually get your Listfiles from the Optional object
                            logger.info("/api/listfiles/executeevalscript post   valores para el json existe indice");

                            objListUploadedFilesReflectances.remove(itemlistCheck);
                            setUploadedFilesReflectancefield(key, jsonObjectForKey, keyint, itemlistCheck, 1);
                        }
                    }
                }
            }
        } catch (JSONException err) {
            logger.info("Error: {}" , err.toString());
        }

    }
    private UploadedFilesReflectance findUploadedFilesReflectancerecord(String key){
        UploadedFilesReflectance listini = new UploadedFilesReflectance();
        listini.setKey(-1);
        for (UploadedFilesReflectance p : objListUploadedFilesReflectances) {
            if (p.getKey().equals(Integer.parseInt(key))) {
                listini = p;
            }
        }
        return listini;
    }
    private void setUploadedFilesReflectancefield(String key, JSONObject jsonObject1, String keyint,
                                                  UploadedFilesReflectance listItm  , Integer option) {
        switch (key.toLowerCase()) {
            case STR_LONGITUD:
                listItm.setLongitude(jsonObject1.get(keyint).toString());
                break;
            case STR_LATITUD:
                listItm.setLatitude(jsonObject1.get(keyint).toString());
                break;
            case STR_ID:
                listItm.setId(jsonObject1.get(keyint).toString());
                break;
            case STR_PATH:
                listItm.setPath(jsonObject1.get(keyint).toString());
                break;
            case STR_REFLECTANCE:
                listItm.setReflectance(jsonObject1.get(keyint).toString());
                break;
            case STR_BAND:
                listItm.setBand(jsonObject1.get(keyint).toString());
                break;
            case STR_USERID:
                listItm.setUserid(jsonObject1.get(keyint).toString());
                break;
            case "soc":
                listItm.setSoc(jsonObject1.get(keyint).toString());
                break;
            default:
                listItm.setSoc(String.valueOf(0));
                break;
        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objListUploadedFilesReflectances.add(listItm);

        }else {
            //el elemennto no existe y se añadeç
            listItm.setKey( Integer.parseInt(keyint));
            objListUploadedFilesReflectances.add(listItm);
        }

    }



    //End


    //Inicio
    @GetMapping ("/api/models/list")
    public String listaimodels (Model interfazConPantalla,HttpSession session) {
        //componemos la url
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/models";
        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());


        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put(STR_USERID, superCustomerUserDetails.getUserID());

            //Comprobamos el patron
            //Se invoca a la URL
            logger.info("Post pantalla de busqueda 50");
            Request request1 = new Request(urltext, requestParam);
            String jsonArray = request1.output;
            readAIJson(jsonArray);
            //comprobamos si hay datos
            if (!objListAIModels.isEmpty()) {
                //Se guardan los datos en la tabla

                //Se descargan las imagenes

                //Se muestra el listado
                interfazConPantalla.addAttribute(STR_LISTA, objListAIModels);
                return "aimodels/models";
            } else {
                return STR_AIMODELS_DETALLES_NO_ENCONTRADO;
            }

        } catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            return STR_AIMODELS_DETALLES_NO_ENCONTRADO;
        }

    }
    private void  readAIJson (String jsonArray){
        try {
            JSONObject jsonObject = new JSONObject(jsonArray);
            Iterator<String> keys = jsonObject.keys();

            while (keys.hasNext()) {
                String key = keys.next();
                if (jsonObject.get(key) instanceof JSONObject) {
                    // do something with jsonObject here
                    JSONObject jsonObjectForKey = jsonObject.getJSONObject(key);
                    Iterator<String> keysint = jsonObjectForKey.keys();
                    while (keysint.hasNext()) {
                        String keyint = keysint.next();
                        logger.info("valores para el json");
                        logger.info(KEYLOG , key , keyint ,jsonObjectForKey.get(keyint));
                        AIModels itemlistCheck = findAIModelsrecord(keyint);

                        if (itemlistCheck.getKey().equals(-1)) {
                            setAIModelsfield(key, jsonObjectForKey, keyint, itemlistCheck, 0);
                        } else {
                            // You use this ".get()" method to actually get your Listfiles from the Optional object
                            logger.info("/api/listfiles/executeevalscript post   valores para el json existe indice");

                            objListAIModels.remove(itemlistCheck);
                            setAIModelsfield(key, jsonObjectForKey, keyint, itemlistCheck, 1);
                        }
                    }
                }
            }
        } catch (JSONException err) {
            logger.info("Error: {}" , err.toString());
        }
    }
    private AIModels findAIModelsrecord(String key){
        AIModels listini = new AIModels();
        listini.setKey(-1);
        for (AIModels p : objListAIModels) {
            if (p.getKey().equals(Integer.parseInt(key))) {
                listini = p;
            }
        }
        return listini;
    }
    private void setAIModelsfield(String key, JSONObject jsonObject1, String keyint,
                                  AIModels listItm  , Integer option) {
        switch (key.toLowerCase()) {
            case "referencia":
                listItm.setReferencia(jsonObject1.get(keyint).toString());
                break;
            case "elemento":
                listItm.setElemento(jsonObject1.get(keyint).toString());
                break;
            case "rmse":
                listItm.setRmse(jsonObject1.get(keyint).toString());
                break;
            case "mae":
                listItm.setMae(jsonObject1.get(keyint).toString());
                break;
            case "r2":
                listItm.setR2(jsonObject1.get(keyint).toString());
                break;
            case "pearson":
                listItm.setPearson(jsonObject1.get(keyint).toString());
                break;
            case "url":
                listItm.setUrl(jsonObject1.get(keyint).toString());
                break;
            default:
                listItm.setUrl("N/A");
                break;
        }
        if (option > 0){
            //el elemennto existe y se sustituye
            objListAIModels.add(listItm);

        }else {
            //el elemennto no existe y se añadeç
            listItm.setKey( Integer.parseInt(keyint));
            objListAIModels.add(listItm);
        }

    }


    @GetMapping ("/api/ai/models/{ref}/ejecutar")
    public String querypoint (@PathVariable("ref") String ref,Model interfazConPantalla,HttpSession session)  {
        QuerySocDto querySocDto = new QuerySocDto();
        querySocDto.setReference(ref);
        interfazConPantalla.addAttribute(STR_DATOS,querySocDto);

        return "aimodels/query";
    }

    @PostMapping("/api/ai/models/{ref}/ejecutar")
    public String querypointPost (@PathVariable("ref") String ref,QuerySocDto querySocDtoEntrada, Model interfazConPantalla,HttpSession session)  {
        //provisional
        String aux = "";
        if (ref.contains("knn")){
            aux = "knn";
        } else if (ref.contains("svr")) {
            aux = "svr";
        }
        //componemos la url
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/ai/pred/" + aux;
        //Obtenemos los datos del usuario de la sesión

        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        logger.info(superCustomerUserDetails.getUsername());


        try {
            JSONObject requestParam = new JSONObject();
            requestParam.put("elem",9);
            requestParam.put("pointid",querySocDtoEntrada.getPointId());
            requestParam.put("fechaIni",querySocDtoEntrada.getFechaIni());
            requestParam.put("fechaFin",querySocDtoEntrada.getFechaFin());
            requestParam.put("longitude",querySocDtoEntrada.getLongitude());
            requestParam.put("latitude",querySocDtoEntrada.getLatitude());
            requestParam.put(STR_OFFSET,configuationProperties.getOffset());
            requestParam.put(STR_CLOUDCOVER,querySocDtoEntrada.getCloudcover());
            requestParam.put("numberOfGeeImages",configuationProperties.getNumberOfGeeImages());
            requestParam.put(STR_REFERENCE,ref);

            //Se invoca a la URL
            logger.info("Post pantalla de busqueda 550");
            Request request1 = new Request(urltext, requestParam);
            String jsonArray = request1.output;

            querySocDtoEntrada.setSoc(jsonArray);
            interfazConPantalla.addAttribute(STR_DATOS,querySocDtoEntrada);


            return "aimodels/query";

        }
        catch (Exception e) {
            logger.info(STR_ERRORMSG);
            logger.info(e.getClass().getSimpleName());
            logger.info(e.getMessage());
            interfazConPantalla.addAttribute(STR_RESULTADO, STR_ERRORMSG + e.getClass().getSimpleName() + e.getMessage());
            return STR_AIMODELS_DETALLES_NO_ENCONTRADO;
        }


    }




    @GetMapping("/api/test")
    public String testapicall(ModelMap interfazConPantalla) throws IOException {
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/listar?reference=02_UBU";
        URL url = new URL(urltext);

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.connect();


        //Getting the response code
        int responsecode = conn.getResponseCode();
        if (responsecode != 200) {
            interfazConPantalla.addAttribute(STR_RESULTADO,"Error en la llamada al api response code:" + responsecode );
        } else {

            StringBuilder inline = new StringBuilder("");
            Scanner scanner = new Scanner(url.openStream());

            //Write all the JSON data into a string using a scanner
            while (scanner.hasNext()) {

                inline.append(scanner.nextLine());
            }

            //Close the scanner
            scanner.close();
            interfazConPantalla.addAttribute(STR_RESULTADO,inline);
        }

        return "api/mostrarresultadoapi";
    }



    @GetMapping("/api/testlist")
    public String testapilist(ModelMap interfazConPantalla) throws IOException {
        String urltext = STR_HTTP + configuationProperties.getIppythonserver() + ":8100/api/listar?reference=02_UBU";
        URL url = new URL(urltext);

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.connect();


        //Getting the response code
        int responsecode = conn.getResponseCode();
        if (responsecode != 200) {
            interfazConPantalla.addAttribute(STR_RESULTADO,"Error en la llamada al api");
        } else {

            StringBuilder inline = new StringBuilder();
            Scanner scanner = new Scanner(url.openStream());

            //Write all the JSON data into a string using a scanner
            while (scanner.hasNext()) {
                inline.append(scanner.nextLine());
            }

            //Close the scanner
            scanner.close();
            interfazConPantalla.addAttribute(STR_RESULTADO,inline);
        }
        return "usuarios/mostrarresultadoapi";
    }
}
